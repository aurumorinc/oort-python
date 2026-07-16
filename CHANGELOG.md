# Changelog v0.8.0

## Breaking Changes

*   **Removal of async-specific API aliases**
    The `aupload`, `agenerate_presigned_url`, and `awebhook_dispatch` methods have been removed in favor of unified function calls.
    *   **Migration Guide:** Replace all instances of `aupload`, `agenerate_presigned_url`, and `awebhook_dispatch` with `upload`, `generate_presigned_url`, and `webhook_dispatch` respectively. If your integration requires specific async handling, use the new `is_async_context()` helper to detect the execution environment.
    *   **Commits:** [bb2bbe3](https://github.com/aurumorinc/oort-python/commit/bb2bbe3c), [6eaf018](https://github.com/aurumorinc/oort-python/commit/6eaf018a), [f57d421](https://github.com/aurumorinc/oort-python/commit/f57d4214)

## New Features

*   **Async Context Detection**
    Implemented `is_async_context()` to automatically detect and handle sync/async execution paths, facilitating the transition to the unified API.
    *   **Commits:** [bb2bbe3](https://github.com/aurumorinc/oort-python/commit/bb2bbe3c), [6eaf018](https://github.com/aurumorinc/oort-python/commit/6eaf018a), [f57d421](https://github.com/aurumorinc/oort-python/commit/f57d4214)

## Improvements

*   **Webhook Dispatch Test Standardization**
    Standardized webhook dispatch tests and updated associated test fixtures to improve reliability.
    *   **Commits:** [f207330](https://github.com/aurumorinc/oort-python/commit/f2073307), [5f29e15](https://github.com/aurumorinc/oort-python/commit/5f29e152), [1e9d936](https://github.com/aurumorinc/oort-python/commit/1e9d9366)
*   **Codebase Formatting**
    Applied PEP 8 style guidelines across the entire codebase to ensure consistent code quality.
    *   **Commits:** [0d4b939](https://github.com/aurumorinc/oort-python/commit/0d4b939e), [aaa78c9](https://github.com/aurumorinc/oort-python/commit/aaa78c9a)
