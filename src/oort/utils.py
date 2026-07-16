import asyncio


def is_async_context() -> bool:
    """Returns True if called from within a running asyncio event loop."""
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False
