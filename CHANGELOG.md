# Changelog v0.4.0

## Breaking Changes

* **Webhook Schema Restructuring**
  The `WebhookResponse` model has been restructured to include a `success` status field, a `delivery_id`, and a standardized `type` field.
  *Migration:* Update all webhook consumers to parse the new response structure.
  *Commits:* [a715677](https://github.com/aurumorinc/oort-python/commit/a7156779), [0466a58](https://github.com/aurumorinc/oort-python/commit/0466a586)

* **WebhookEvent Enum Case Sensitivity**
  The `WebhookEvent` enum values have been updated to lowercase to ensure consistency across the API.
  *Migration:* Update all references to `WebhookEvent` members to use lowercase (e.g., `WebhookEvent.USER_CREATED` becomes `WebhookEvent.user_created`).
  *Commits:* [a715677](https://github.com/aurumorinc/oort-python/commit/a7156779), [0466a58](https://github.com/aurumorinc/oort-python/commit/0466a586)

* **WebhookRequest URL Type Enforcement**
  The `WebhookRequest.url` field now strictly requires an `HttpUrl` object instead of a raw string.
  *Migration:* Ensure all `WebhookRequest` instantiations pass an `HttpUrl` object for the `url` parameter.
  *Commits:* [a715677](https://github.com/aurumorinc/oort-python/commit/a7156779), [0466a58](https://github.com/aurumorinc/oort-python/commit/0466a586)

* **Introduction of _serialize_files Helper**
  A new `_serialize_files` helper method has been added to the webhook serialization logic, which may affect custom serialization overrides.
  *Commits:* [a715677](https://github.com/aurumorinc/oort-python/commit/a7156779), [0466a58](https://github.com/aurumorinc/oort-python/commit/0466a586)

## Other

* **Standardization of Import Statements**
  Refactored import statements across the codebase to ensure consistent formatting.
  *Commits:* [197f2cd](https://github.com/aurumorinc/oort-python/commit/197f2cd8), [2c98f5e](https://github.com/aurumorinc/oort-python/commit/2c98f5e2), [5c85473](https://github.com/aurumorinc/oort-python/commit/5c854733)

* **Formatting of __all__ Lists**
  Updated `__all__` list formatting to use multi-line structures and double quotes for improved readability and consistency.
  *Commits:* [197f2cd](https://github.com/aurumorinc/oort-python/commit/197f2cd8), [2c98f5e](https://github.com/aurumorinc/oort-python/commit/2c98f5e2), [5c85473](https://github.com/aurumorinc/oort-python/commit/5c854733)
