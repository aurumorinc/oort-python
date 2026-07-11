# src/oort/webhook/service.py
import asyncio
import functools
import inspect
import threading
from typing import Any, Callable, Optional
import uuid

import httpx
import logging

from oort.webhook.schema import WebhookRequest, WebhookEvent, WebhookResponse

logger = logging.getLogger(__name__)


async def dispatch_webhook(
    webhook: Optional[WebhookRequest], payload: WebhookResponse
) -> None:
    """Trigger an HTTP callback based on the webhook spec asynchronously."""
    if not webhook:
        return

    headers = webhook.headers or {}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=webhook.method,
                url=webhook.url,
                json=payload.model_dump(exclude_none=True),
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
    except Exception as e:
        logger.warning("Failed to trigger webhook for event %s: %s", payload.event, e)


def _sync_dispatch(webhook: Optional[WebhookRequest], payload: WebhookResponse) -> None:
    """Helper to run dispatch_webhook synchronously in a thread (or event loop)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We are already in an event loop, but running synchronous code.
        # Fire and wait safely using a thread.
        def run_in_thread():
            asyncio.run(dispatch_webhook(webhook, payload))

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()
    else:
        asyncio.run(dispatch_webhook(webhook, payload))


def webhook_dispatch(
    event_prefix: str = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to handle webhook lifecycle events (STARTED, COMPLETED, FAILED)."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        is_async = inspect.iscoroutinefunction(func)

        if is_async:

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                webhook_data = bound_args.arguments.get("webhook")
                webhook = None
                if isinstance(webhook_data, dict):
                    webhook = WebhookRequest(**webhook_data)
                elif isinstance(webhook_data, WebhookRequest):
                    webhook = webhook_data

                task_id = uuid.uuid4().hex

                if webhook and (
                    not webhook.events or WebhookEvent.STARTED in webhook.events
                ):
                    payload = WebhookResponse(
                        event=f"{event_prefix}.{WebhookEvent.STARTED.value}"
                        if event_prefix
                        else WebhookEvent.STARTED.value,
                        task_id=task_id,
                        metadata=webhook.metadata,
                        data=None,
                        error=None,
                    )
                    await dispatch_webhook(webhook=webhook, payload=payload)

                try:
                    response = await func(*args, **kwargs)
                except Exception as e:
                    if webhook and (
                        not webhook.events or WebhookEvent.FAILED in webhook.events
                    ):
                        payload = WebhookResponse(
                            event=f"{event_prefix}.{WebhookEvent.FAILED.value}"
                            if event_prefix
                            else WebhookEvent.FAILED.value,
                            task_id=task_id,
                            metadata=webhook.metadata,
                            data=None,
                            error=str(e),
                        )
                        await dispatch_webhook(webhook=webhook, payload=payload)
                    raise e

                success = getattr(response, "success", True)
                event = WebhookEvent.COMPLETED if success else WebhookEvent.FAILED

                if webhook and (not webhook.events or event in webhook.events):
                    # extract data
                    if isinstance(response, dict):
                        data = response.get("output", response)
                    elif hasattr(response, "output"):
                        data = response.output
                    elif hasattr(response, "model_dump"):
                        data = response.model_dump()
                    elif hasattr(response, "dict"):
                        data = response.dict()
                    else:
                        data = response

                    payload = WebhookResponse(
                        event=f"{event_prefix}.{event.value}"
                        if event_prefix
                        else event.value,
                        task_id=task_id,
                        metadata=webhook.metadata,
                        data=data,
                        error=getattr(response, "error", None) if not success else None,
                    )
                    await dispatch_webhook(webhook=webhook, payload=payload)

                return response

            return async_wrapper

        else:

            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                webhook_data = bound_args.arguments.get("webhook")
                webhook = None
                if isinstance(webhook_data, dict):
                    webhook = WebhookRequest(**webhook_data)
                elif isinstance(webhook_data, WebhookRequest):
                    webhook = webhook_data

                task_id = uuid.uuid4().hex

                if webhook and (
                    not webhook.events or WebhookEvent.STARTED in webhook.events
                ):
                    payload = WebhookResponse(
                        event=f"{event_prefix}.{WebhookEvent.STARTED.value}"
                        if event_prefix
                        else WebhookEvent.STARTED.value,
                        task_id=task_id,
                        metadata=webhook.metadata,
                        data=None,
                        error=None,
                    )
                    _sync_dispatch(webhook=webhook, payload=payload)

                try:
                    response = func(*args, **kwargs)
                except Exception as e:
                    if webhook and (
                        not webhook.events or WebhookEvent.FAILED in webhook.events
                    ):
                        payload = WebhookResponse(
                            event=f"{event_prefix}.{WebhookEvent.FAILED.value}"
                            if event_prefix
                            else WebhookEvent.FAILED.value,
                            task_id=task_id,
                            metadata=webhook.metadata,
                            data=None,
                            error=str(e),
                        )
                        _sync_dispatch(webhook=webhook, payload=payload)
                    raise e

                success = getattr(response, "success", True)
                event = WebhookEvent.COMPLETED if success else WebhookEvent.FAILED

                if webhook and (not webhook.events or event in webhook.events):
                    # extract data
                    if isinstance(response, dict):
                        data = response.get("output", response)
                    elif hasattr(response, "output"):
                        data = response.output
                    elif hasattr(response, "model_dump"):
                        data = response.model_dump()
                    elif hasattr(response, "dict"):
                        data = response.dict()
                    else:
                        data = response

                    payload = WebhookResponse(
                        event=f"{event_prefix}.{event.value}"
                        if event_prefix
                        else event.value,
                        task_id=task_id,
                        metadata=webhook.metadata,
                        data=data,
                        error=getattr(response, "error", None) if not success else None,
                    )
                    _sync_dispatch(webhook=webhook, payload=payload)

                return response

            return sync_wrapper

    return decorator


__all__ = ["dispatch_webhook", "webhook_dispatch"]
