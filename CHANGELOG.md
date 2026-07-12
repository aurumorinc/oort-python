# Changelog v0.5.0

## Improvements

### Configuration Management
* **Flattened S3 configuration in OortSettings**
  The S3 configuration structure within `OortSettings` has been flattened into top-level fields to simplify configuration management. Backward compatibility is maintained via a computed `s3` property, ensuring existing integrations will continue to function without immediate modification.
  Commits: [f399daf](https://github.com/aurumorinc/oort-python/commit/f399dafd), [746e113](https://github.com/aurumorinc/oort-python/commit/746e1132), [1f47a91](https://github.com/aurumorinc/oort-python/commit/1f47a912)
