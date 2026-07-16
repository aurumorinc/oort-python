# Changelog v0.7.0

## Breaking Changes

* **Standardized sync/async naming conventions and split webhook logic**
  The API structure has been refactored to clearly separate synchronous and asynchronous operations, and webhook logic has been decoupled.
  Commits: [c42ca38](https://github.com/aurumorinc/oort-python/commit/c42ca38a), [4594fab](https://github.com/aurumorinc/oort-python/commit/4594fab9), [051354d](https://github.com/aurumorinc/oort-python/commit/051354d4)

* **Renamed public API functions to distinguish sync/async operations**
  Public methods have been renamed to enforce a strict naming convention.
  * Migration Guide:
    * Update all asynchronous calls from `upload` to `aupload`.
    * Synchronous calls should now use `upload`.
    * Update `dispatch_webhook` to `adispatch_webhook`.
    * Update `get_presigned_url` to `generate_presigned_url`.
  Severity: High.

## Improvements

* **Isolated environment variables for test reliability**
  Test suites now utilize isolated environment variables to prevent cross-test contamination.
  Commit: [c5ef313](https://github.com/aurumorinc/oort-python/commit/c5ef313f)

* **Added S3 integration tests**
  New integration tests have been implemented to validate S3 interactions.
  Commits: [227eeef](https://github.com/aurumorinc/oort-python/commit/227eeef0), [ea7ea86](https://github.com/aurumorinc/oort-python/commit/ea7ea862)

## Infrastructure

* **Added vcrpy 8.3.0 for HTTP mocking**
  Integrated `vcrpy` version 8.3.0 into the development environment to improve HTTP request mocking capabilities.
  Commit: [94332b6](https://github.com/aurumorinc/oort-python/commit/94332b68)

## Other

* **Codebase cleanup of imports and exports**
  Sorted imports and standardized `__all__` exports across the codebase to ensure consistency.
  Commit: [779a3b7](https://github.com/aurumorinc/oort-python/commit/779a3b7a)
