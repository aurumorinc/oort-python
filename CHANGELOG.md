# Changelog v0.3.0

## Breaking Changes

*   **Configuration Refactor: Unified `OortSettings` inheritance**
    The internal inheritance structure for `OortSettings` has been unified to improve consistency across the configuration layer.
    Commits: [371162f](https://github.com/aurumorinc/oort-python/commit/371162f0), [dffbffd](https://github.com/aurumorinc/oort-python/commit/dffbffda)

*   **Configuration API Change: Rename `settings.oort_s3` to `settings.s3`**
    The `settings.oort_s3` attribute has been removed. All references must be updated to `settings.s3`.
    *   **Migration Path:**
        Before:
        ```python
        # Old configuration
        s3_config = settings.oort_s3.bucket_name
        ```
        After:
        ```python
        # New configuration
        s3_config = settings.s3.bucket_name
        ```
    Commits: [371162f](https://github.com/aurumorinc/oort-python/commit/371162f0), [dffbffd](https://github.com/aurumorinc/oort-python/commit/dffbffda)
