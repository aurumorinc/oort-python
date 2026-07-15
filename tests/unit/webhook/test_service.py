import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
import time
from pydantic import BaseModel
from oort.webhook.service import (
    dispatch_webhook,
    webhook_dispatch,
    _serialize_files,
    _serialize_files_async,
)
from oort.webhook.schema import WebhookRequest, WebhookResponse, WebhookEvent


@pytest.fixture
def webhook():
    return WebhookRequest(
        url="https://example.com/webhook",
        events=[WebhookEvent.STARTED, WebhookEvent.COMPLETED],
    )


class MockResponseModel(BaseModel):
    success: bool
    output: dict


@patch("oort.webhook.service.httpx.AsyncClient", spec=True)
@pytest.mark.asyncio
async def test_dispatch_webhook(mock_client_cls, webhook):
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_client.request.return_value = mock_response

    # async with mock
    mock_client_cls.return_value.__aenter__.return_value = mock_client

    payload = WebhookResponse(
        success=True,
        type="started",
        id="123",
        webhookId="456",
        data=[],
    )

    await dispatch_webhook(webhook, payload)

    mock_client.request.assert_called_once_with(
        method="POST",
        url="https://example.com/webhook",
        json={
            "success": True,
            "type": "started",
            "id": "123",
            "webhookId": "456",
            "data": [],
        },
        headers={},
        timeout=10.0,
    )


@patch("oort.webhook.service.dispatch_webhook")
@pytest.mark.asyncio
async def test_webhook_dispatch_async(mock_dispatch, webhook):
    @webhook_dispatch(event_prefix="test")
    async def dummy_async_func(data: str, webhook: WebhookRequest = None):
        return MockResponseModel(success=True, output={"result": data})

    res = await dummy_async_func("test", webhook=webhook)
    assert res.success is True

    # Check that dispatch_webhook was called for STARTED and COMPLETED
    assert mock_dispatch.call_count == 2

    call1 = mock_dispatch.call_args_list[0]
    assert call1.kwargs["payload"].type == "test.started"

    call2 = mock_dispatch.call_args_list[1]
    assert call2.kwargs["payload"].type == "test.completed"


@patch("oort.webhook.service._sync_dispatch")
def test_webhook_dispatch_sync(mock_dispatch, webhook):
    @webhook_dispatch(event_prefix="test")
    def dummy_sync_func(data: str, webhook: WebhookRequest = None):
        return MockResponseModel(success=True, output={"result": data})

    res = dummy_sync_func("test", webhook=webhook)
    assert res.success is True

    assert mock_dispatch.call_count == 2
    call1 = mock_dispatch.call_args_list[0]
    assert call1.kwargs["payload"].type == "test.started"

    call2 = mock_dispatch.call_args_list[1]
    assert call2.kwargs["payload"].type == "test.completed"


def test_serialize_files():
    class DummyFile:
        def __init__(self, filename, mimetype, presigned_url):
            self.filename = filename
            self.mimetype = mimetype
            self.presigned_url = presigned_url

    f = DummyFile("test.png", "image/png", "https://s3/test.png")

    # Test single file
    res = _serialize_files(f)
    assert res == {
        "filename": "test.png",
        "mimetype": "image/png",
        "url": "https://s3/test.png",
    }

    # Test list of files
    res = _serialize_files([f, f])
    assert res == [
        {"filename": "test.png", "mimetype": "image/png", "url": "https://s3/test.png"},
        {"filename": "test.png", "mimetype": "image/png", "url": "https://s3/test.png"},
    ]

    # Test dictionary containing files
    res = _serialize_files({"file": f, "other": "value"})
    assert res == {
        "file": {
            "filename": "test.png",
            "mimetype": "image/png",
            "url": "https://s3/test.png",
        },
        "other": "value",
    }


class AsyncDummyFile:
    def __init__(
        self,
        filename="test.png",
        mimetype="image/png",
        presigned_url="https://s3/test.png",
        delay=0.0,
    ):
        self.filename = filename
        self.mimetype = mimetype
        self._presigned_url = presigned_url
        self.delay = delay

    async def get_presigned_url_async(self):
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        if isinstance(self._presigned_url, Exception):
            raise self._presigned_url
        return self._presigned_url


@pytest.mark.asyncio
async def test_serialize_files_async_single():
    f = AsyncDummyFile()
    res = await _serialize_files_async(f)
    assert res == {
        "filename": "test.png",
        "mimetype": "image/png",
        "url": "https://s3/test.png",
    }


@pytest.mark.asyncio
async def test_serialize_files_async_list():
    f = AsyncDummyFile()
    res = await _serialize_files_async([f, f])
    expected = {
        "filename": "test.png",
        "mimetype": "image/png",
        "url": "https://s3/test.png",
    }
    assert res == [expected, expected]


@pytest.mark.asyncio
async def test_serialize_files_async_dict():
    f = AsyncDummyFile()
    res = await _serialize_files_async({"file": f, "other": "value"})
    assert res == {
        "file": {
            "filename": "test.png",
            "mimetype": "image/png",
            "url": "https://s3/test.png",
        },
        "other": "value",
    }


@pytest.mark.asyncio
async def test_serialize_files_async_mixed_and_nested():
    f = AsyncDummyFile()
    complex_data = {
        "list_of_files": [f, {"nested": f}],
        "string": "test",
        "integer": 123,
        "empty_list": [],
        "empty_dict": {},
    }
    res = await _serialize_files_async(complex_data)

    expected_f = {
        "filename": "test.png",
        "mimetype": "image/png",
        "url": "https://s3/test.png",
    }
    assert res == {
        "list_of_files": [expected_f, {"nested": expected_f}],
        "string": "test",
        "integer": 123,
        "empty_list": [],
        "empty_dict": {},
    }


@pytest.mark.asyncio
async def test_serialize_files_async_missing_attributes():
    class IncompleteFile:
        async def get_presigned_url_async(self):
            return "https://example.com"

    f = IncompleteFile()
    res = await _serialize_files_async(f)
    assert res is f  # Passes through untouched


@pytest.mark.asyncio
async def test_serialize_files_async_upload_failure():
    f = AsyncDummyFile(presigned_url=Exception("Mock S3 Error"))
    with pytest.raises(Exception, match="Mock S3 Error"):
        await _serialize_files_async(f)


@pytest.mark.asyncio
async def test_serialize_files_async_concurrency_timing():
    delay = 0.1
    files = [AsyncDummyFile(delay=delay) for _ in range(5)]

    start_time = time.monotonic()
    await _serialize_files_async(files)
    duration = time.monotonic() - start_time

    # If sequential, it would take 0.5s. If concurrent, it should take ~0.1s.
    assert duration < 0.25, f"Expected concurrent execution, but took {duration:.2f}s"
