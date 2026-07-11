import threading
import requests
from functools import wraps
from typing import Any, Callable, Optional, Dict, List
from pydantic import BaseModel
from python_logging.main import get_logger

logger = get_logger(__name__)

class WebhookSuccessPayload(BaseModel):
    status: str = "success"
    filename: Optional[str] = None
    mimetype: Optional[str] = None
    url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None

class WebhookErrorPayload(BaseModel):
    status: str = "error"
    message: str

def _send_webhook(url: str, payload: dict) -> None:
    """Sends the webhook payload in a background thread."""
    try:
        logger.info(f"Sending webhook to {url}")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Webhook sent successfully to {url}")
    except requests.RequestException as e:
        logger.warning(f"Failed to call webhook {url}: {e}")

def webhook_response(func: Callable) -> Callable:
    """
    Decorator that intercepts the return value or exception of a function
    and sends it to a webhook URL if `callback_url` is present in the first argument.
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        callback_url = getattr(request, 'callback_url', None)
        
        try:
            result = func(request, *args, **kwargs)
            
            if callback_url:
                # Handle single File result
                if hasattr(result, 'filename') and hasattr(result, 'mimetype'):
                    payload = WebhookSuccessPayload(
                        filename=result.filename,
                        mimetype=result.mimetype,
                        url=result.presigned_url,
                        metadata=getattr(request, 'metadata', None)
                    ).model_dump(exclude_none=True)
                # Handle List[File] result (batch)
                elif isinstance(result, list):
                    results_list = []
                    for i, res in enumerate(result):
                        item = {
                            "filename": getattr(res, 'filename', None),
                            "mimetype": getattr(res, 'mimetype', None),
                            "url": getattr(res, 'presigned_url', None)
                        }
                        # Try to match metadata from batch requests
                        if hasattr(request, 'requests') and i < len(request.requests):
                            orig_req = request.requests[i]
                            if getattr(orig_req, 'metadata', None):
                                item["metadata"] = orig_req.metadata
                        results_list.append({k: v for k, v in item.items() if v is not None})
                        
                    payload = WebhookSuccessPayload(
                        results=results_list
                    ).model_dump(exclude_none=True)
                else:
                    # Fallback for unknown return types
                    payload = WebhookSuccessPayload().model_dump(exclude_none=True)
                    
                threading.Thread(target=_send_webhook, args=(callback_url, payload), daemon=True).start()
                
            return result
            
        except Exception as e:
            if callback_url:
                payload = WebhookErrorPayload(message=str(e)).model_dump()
                threading.Thread(target=_send_webhook, args=(callback_url, payload), daemon=True).start()
            raise e
            
    return wrapper
