from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WebhookEvent(str, Enum):
    """Lifecycle events for webhook callbacks."""

    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WebhookRequest(BaseModel):
    """A webhook configuration for receiving asynchronous task updates."""

    url: str = Field(..., description="The URL to send the webhook payload to.")
    method: str = Field(
        "POST", description="The HTTP method to use (defaults to POST)."
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None, description="Optional headers to include in the webhook request."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata to include in the payload."
    )
    events: Optional[List[WebhookEvent]] = Field(
        default=None,
        description="Optional list of events to subscribe to. If not provided, defaults to all.",
    )


class WebhookResponse(BaseModel):
    """Standardized response payload sent to the webhook URL."""

    event: str = Field(
        ...,
        description="The event that triggered the webhook (e.g., STARTED, COMPLETED, FAILED).",
    )
    task_id: str = Field(..., description="A unique identifier for the task.")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Custom metadata provided in the request."
    )
    data: Optional[Any] = Field(None, description="The result data (if successful).")
    error: Optional[str] = Field(None, description="Error message (if failed).")


__all__ = ["WebhookEvent", "WebhookRequest", "WebhookResponse"]
