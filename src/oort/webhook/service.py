# src/oort/webhook/service.py
import asyncio
import functools
import inspect
from typing import Any, Callable, Optional
import uuid

import httpx
import logging

from oort.webhook.schema import WebhookRequest, WebhookEvent, WebhookResponse

logger = logging.getLogger(__name__)


def _extract_webhook_and_bind_args(
    sig: inspect.Signature, args: tuple, kwargs: dict
) -> tuple[inspect.BoundArguments, Optional[WebhookRequest]]:
    """Helper to extract webhook from function arguments."""
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    webhook_data = bound_args.arguments.get("webhook")
    webhook = None
    if isinstance(webhook_data, dict):
        webhook = WebhookRequest(**webhook_data)
    elif isinstance(webhook_data, WebhookRequest):
        webhook = webhook_data

    return bound_args, webhook


def _create_payload(
    event: WebhookEvent,
    event_prefix: str,
    task_id: str,
    webhook: WebhookRequest,
    success: bool = True,
    data: Any = None,
    error: Optional[str] = None,
) -> WebhookResponse:
    """Helper to create the WebhookResponse payload."""
    type_str = f"{event_prefix}.{event.value}" if event_prefix else event.value
    return WebhookResponse(
        success=success,
        type=type_str,
        id=task_id,
        webhookId=uuid.uuid4().hex,
        data=data if data is not None else [],
        metadata=webhook.metadata,
        error=error,
    )


def _extract_response_data(response: Any) -> Any:
    """Helper to extract data/output from a response object."""
    if isinstance(response, dict):
        return response.get("output", response)
    if hasattr(response, "output"):
        return response.output
    if hasattr(response, "model_dump"):
        return response.model_dump()
    if hasattr(response, "dict"):
        return response.dict()
    return response


def _serialize_files(obj: Any) -> Any:
    """Recursively converts File objects into dicts for JSON serialization."""
    if isinstance(obj, list):
        return [_serialize_files(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _serialize_files(v) for k, v in obj.items()}
    if hasattr(obj, "mimetype") and hasattr(obj, "filename"):
        try:
            url = obj.presigned_url
            return {
                "filename": obj.filename,
                "mimetype": obj.mimetype,
                "url": url,
            }
        except AttributeError:
            pass

    return obj


async def _aserialize_files(obj: Any) -> Any:
    """Recursively converts File objects into dicts for JSON serialization asynchronously."""
    if isinstance(obj, list):
        if not obj:
            return []
        return list(await asyncio.gather(*[_aserialize_files(i) for i in obj]))
    if isinstance(obj, dict):
        if not obj:
            return {}
        keys = list(obj.keys())
        values = await asyncio.gather(*[_aserialize_files(obj[k]) for k in keys])
        return dict(zip(keys, values))

    if hasattr(obj, "mimetype") and hasattr(obj, "filename"):
        try:
            url = obj.presigned_url
            if inspect.isawaitable(url):
                url = await url
            return {
                "filename": obj.filename,
                "mimetype": obj.mimetype,
                "url": url,
            }
        except AttributeError:
            pass

    return obj


def _extract_webhook_and_bind_args(
    sig: inspect.Signature, args: tuple, kwargs: dict
) -> tuple[inspect.BoundArguments, Optional[WebhookRequest]]:
    """Helper to extract webhook from function arguments."""
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    webhook_data = bound_args.arguments.get("webhook")
    webhook = None
    if isinstance(webhook_data, dict):
        webhook = WebhookRequest(**webhook_data)
    elif isinstance(webhook_data, WebhookRequest):
        webhook = webhook_data

    return bound_args, webhook


def _create_payload(
    event: WebhookEvent,
    event_prefix: str,
    task_id: str,
    webhook: WebhookRequest,
    success: bool = True,
    data: Any = None,
    error: Optional[str] = None,
) -> WebhookResponse:
    """Helper to create the WebhookResponse payload."""
    type_str = f"{event_prefix}.{event.value}" if event_prefix else event.value
    return WebhookResponse(
        success=success,
        type=type_str,
        id=task_id,
        webhookId=uuid.uuid4().hex,
        data=data if data is not None else [],
        metadata=webhook.metadata,
        error=error,
    )


def _extract_response_data(response: Any) -> Any:
    """Helper to extract data/output from a response object."""
    if isinstance(response, dict):
        return response.get("output", response)
    if hasattr(response, "output"):
        return response.output
    if hasattr(response, "model_dump"):
        return response.model_dump()
    if hasattr(response, "dict"):
        return response.dict()
    return response


async def adispatch_webhook(
    webhook: Optional[WebhookRequest], payload: WebhookResponse
) -> None:
    """Trigger an HTTP callback based on the webhook spec asynchronously."""
    if not webhook:
        return

    headers = webhook.headers or {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method="POST",
                url=str(webhook.url),
                json=payload.model_dump(exclude_none=True),
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as e:
        logger.warning("Failed to trigger webhook for event %s: %s", payload.type, e)


def dispatch_webhook(
    webhook: Optional[WebhookRequest], payload: WebhookResponse
) -> None:
    """Trigger an HTTP callback based on the webhook spec synchronously."""
    if not webhook:
        return

    headers = webhook.headers or {}

    try:
        with httpx.Client() as client:
            response = client.request(
                method="POST",
                url=str(webhook.url),
                json=payload.model_dump(exclude_none=True),
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as e:
        logger.warning("Failed to trigger webhook for event %s: %s", payload.type, e)


def webhook_dispatch(
    event_prefix: str = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to handle webhook lifecycle events (STARTED, COMPLETED, FAILED). Routes automatically."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)
        is_async = inspect.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                _, webhook = _extract_webhook_and_bind_args(sig, args, kwargs)
                task_id = uuid.uuid4().hex

                if webhook and (
                    not webhook.events or WebhookEvent.STARTED in webhook.events
                ):
                    payload = _create_payload(
                        WebhookEvent.STARTED, event_prefix, task_id, webhook
                    )
                    await adispatch_webhook(webhook=webhook, payload=payload)

                try:
                    response = await func(*args, **kwargs)
                except Exception as e:
                    if webhook and (
                        not webhook.events or WebhookEvent.FAILED in webhook.events
                    ):
                        payload = _create_payload(
                            WebhookEvent.FAILED,
                            event_prefix,
                            task_id,
                            webhook,
                            success=False,
                            error=str(e),
                        )
                        await adispatch_webhook(webhook=webhook, payload=payload)
                    raise e

                success = getattr(response, "success", True)
                event = WebhookEvent.COMPLETED if success else WebhookEvent.FAILED

                if webhook and (not webhook.events or event in webhook.events):
                    data = _extract_response_data(response)
                    payload = _create_payload(
                        event,
                        event_prefix,
                        task_id,
                        webhook,
                        success=success,
                        data=await _aserialize_files(data) if data is not None else [],
                        error=getattr(response, "error", None) if not success else None,
                    )
                    await adispatch_webhook(webhook=webhook, payload=payload)

                return response

            return async_wrapper

        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                _, webhook = _extract_webhook_and_bind_args(sig, args, kwargs)
                task_id = uuid.uuid4().hex

                if webhook and (
                    not webhook.events or WebhookEvent.STARTED in webhook.events
                ):
                    payload = _create_payload(
                        WebhookEvent.STARTED, event_prefix, task_id, webhook
                    )
                    dispatch_webhook(webhook=webhook, payload=payload)

                try:
                    response = func(*args, **kwargs)
                except Exception as e:
                    if webhook and (
                        not webhook.events or WebhookEvent.FAILED in webhook.events
                    ):
                        payload = _create_payload(
                            WebhookEvent.FAILED,
                            event_prefix,
                            task_id,
                            webhook,
                            success=False,
                            error=str(e),
                        )
                        dispatch_webhook(webhook=webhook, payload=payload)
                    raise e

                success = getattr(response, "success", True)
                event = WebhookEvent.COMPLETED if success else WebhookEvent.FAILED

                if webhook and (not webhook.events or event in webhook.events):
                    data = _extract_response_data(response)
                    payload = _create_payload(
                        event,
                        event_prefix,
                        task_id,
                        webhook,
                        success=success,
                        data=_serialize_files(data) if data is not None else [],
                        error=getattr(response, "error", None) if not success else None,
                    )
                    dispatch_webhook(webhook=webhook, payload=payload)

                return response

            return sync_wrapper

    return decorator


__all__ = ["dispatch_webhook", "adispatch_webhook", "webhook_dispatch"]
