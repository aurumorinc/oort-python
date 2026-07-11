# Oort

Oort is a centralized and optimized utility package providing `webhook` dispatching and `file` (S3) operations. Built with Domain-Driven Design (DDD) principles and a pure async core, it provides high-performance and DRY code that seamlessly works with both async and sync codebases.

## Features
- **S3 File Operations**: Lazy S3 uploading, presigned URL generation, and async/sync `File` wrapper.
- **Webhook Dispatch**: Robust webhook delivery for `STARTED`, `COMPLETED`, and `FAILED` task lifecycle events. Supports filtering and metadata injection.
- **Serverless-Safe Sync Bridges**: Dispatches webhooks correctly inside synchronous Serverless environments by safely joining threads.

## Installation

Since `oort` depends on `worldline-python` (which is a git repository), you can install the project like this:

```bash
pdm add "git+https://github.com/aurumorinc/worldline-python.git"
pdm add oort-python
```

## Configuration

`oort` settings are designed to be easily composed within your application.

```python
from worldline.config import WorldlineSettings
from oort.config import OortSettings, setup
from pydantic_settings import BaseSettings

class AppSettings(WorldlineSettings, OortSettings, BaseSettings):
    pass

settings = AppSettings()

# You MUST call setup() to activate the configuration for oort globally
setup(settings)
```

## Usage

### Webhooks

Use `@webhook_dispatch` to automatically manage webhook lifecycles. 

```python
from oort import webhook_dispatch, WebhookRequest, WebhookEvent

# Automatically sends STARTED (if async or joined locally), then COMPLETED or FAILED
@webhook_dispatch(event_prefix="data_extraction")
async def process_data(data: str, webhook: WebhookRequest = None):
    return {"success": True, "output": {"processed": data}}

webhook_config = WebhookRequest(url="https://example.com/webhook", events=[WebhookEvent.COMPLETED])
await process_data("raw data", webhook=webhook_config)
```

**Sync usage is fully supported**, safely bridging to the async dispatch.

### File Operations (S3)

Use `File` as a unified wrapper for Playwright, bytes, paths, and URLs:

```python
from oort import File

# Capture bytes and get a lazily evaluated S3 Presigned URL
with File.from_bytes(b"hello world", "test.txt", "text/plain") as f:
    url = f.presigned_url  # Triggers an upload to S3 and generates a URL safely in sync or async contexts
    print(url)
```

### Direct Async S3 Operations

You can use the native async functions directly for ultimate control:

```python
from oort import upload, generate_presigned_url

await upload(b"my data", "object_key.txt", "text/plain", config=settings.oort_s3)
url = await generate_presigned_url("object_key.txt", config=settings.oort_s3)
```

## Development

- `pdm install -G dev -e .` to setup locally.
- `pdm run pytest tests/ -v` to run tests.
- `pdm run ruff check src` and `pdm run ruff format src` for code linting.
- `pdm run pyrefly check` for static type checking.
