import pytest
import respx
import httpx
from oort.webhook.service import webhook_dispatch
from oort.webhook.schema import WebhookRequest


@pytest.fixture
def webhook():
    return WebhookRequest(url="https://example.com/webhook")


@respx.mock
@pytest.mark.asyncio
async def test_webhook_integration_async(webhook):
    request_mock = respx.post("https://example.com/webhook").mock(
        return_value=httpx.Response(200)
    )

    class AsyncDummyFile:
        def __init__(
            self,
            filename="test.png",
            mimetype="image/png",
            presigned_url="https://s3/test.png",
        ):
            self.filename = filename
            self.mimetype = mimetype
            self._presigned_url = presigned_url

        @property
        async def presigned_url(self):
            return self._presigned_url

    @webhook_dispatch(event_prefix="test")
    async def process_data(data: str, webhook: WebhookRequest = None):
        return {"success": True, "output": {"data": data, "file": AsyncDummyFile()}}

    await process_data("async_hello", webhook=webhook)

    assert request_mock.called
    assert request_mock.call_count == 2

    # Verify payloads
    req1 = request_mock.calls[0].request
    req2 = request_mock.calls[1].request

    import json

    body1 = json.loads(req1.content)
    body2 = json.loads(req2.content)

    assert body1["type"] == "test.started"
    assert body2["type"] == "test.completed"
    assert body2["data"] == {
        "data": "async_hello",
        "file": {
            "filename": "test.png",
            "mimetype": "image/png",
            "url": "https://s3/test.png",
        },
    }


@respx.mock
def test_webhook_integration_sync(webhook):
    request_mock = respx.post("https://example.com/webhook").mock(
        return_value=httpx.Response(200)
    )

    @webhook_dispatch(event_prefix="test")
    def process_data_sync(data: str, webhook: WebhookRequest = None):
        return {"success": True, "output": {"data": data}}

    process_data_sync("sync_hello", webhook=webhook)

    assert request_mock.called
    assert request_mock.call_count == 2

    # Verify payloads
    req1 = request_mock.calls[0].request
    req2 = request_mock.calls[1].request

    import json

    body1 = json.loads(req1.content)
    body2 = json.loads(req2.content)

    assert body1["type"] == "test.started"
    assert body2["type"] == "test.completed"
    assert body2["data"] == {"data": "sync_hello"}
