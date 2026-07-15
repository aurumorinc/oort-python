# Changelog v0.6.0

## Features

* **Async File Serialization for Webhooks**
  Implemented `_serialize_files_async` to handle webhook payloads, enabling recursive processing of file objects and asynchronous generation of presigned URLs.
  Commits: [2eaaaa5](https://github.com/aurumorinc/oort-python/commit/2eaaaa58), [133b8df](https://github.com/aurumorinc/oort-python/commit/133b8df2), [b157094](https://github.com/aurumorinc/oort-python/commit/b157094d)

* **Worldline Configuration Support**
  Integrated `WorldlineSettings` into the `OortSettings` class, allowing for the new configuration structures required for Worldline integration.
  Commits: [2eaaaa5](https://github.com/aurumorinc/oort-python/commit/2eaaaa58), [133b8df](https://github.com/aurumorinc/oort-python/commit/133b8df2), [b157094](https://github.com/aurumorinc/oort-python/commit/b157094d)

## Improvements

* **Expanded Test Coverage**
  Added comprehensive unit tests covering the new configuration and serialization logic to ensure stability.
  Commits: [2eaaaa5](https://github.com/aurumorinc/oort-python/commit/2eaaaa58), [133b8df](https://github.com/aurumorinc/oort-python/commit/133b8df2), [b157094](https://github.com/aurumorinc/oort-python/commit/b157094d)
