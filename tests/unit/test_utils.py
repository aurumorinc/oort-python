import pytest
from oort.utils import is_async_context


def test_is_async_context_sync():
    assert is_async_context() is False


@pytest.mark.asyncio
async def test_is_async_context_async():
    assert is_async_context() is True
