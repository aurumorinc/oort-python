# Changelog v0.8.1

## Improvements

*   **VCR and Test Configuration**
    Implemented request and response body scrubbing for VCR cassettes to prevent sensitive data leakage in test artifacts.
    *Commit: [cca76dc](https://github.com/aurumorinc/oort-python/commit/cca76dc2)*

*   **Multipart Upload Integration Testing**
    Added comprehensive integration tests for multipart upload workflows to ensure stability across high-volume data transfers.
    *Commit: [cca76dc](https://github.com/aurumorinc/oort-python/commit/cca76dc2)*

## Bug Fixes

*   **GCS Checksum Validation**
    Updated S3 client configuration to explicitly enforce checksum handling when interacting with Google Cloud Storage endpoints using SigV4 authentication.
    *Commits: [84b5042](https://github.com/aurumorinc/oort-python/commit/84b5042c), [6414e0d](https://github.com/aurumorinc/oort-python/commit/6414e0d7)*
