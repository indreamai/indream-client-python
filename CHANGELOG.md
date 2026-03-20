# Changelog

All notable changes to `indream-client` are documented in this file.

## 0.2.0 - 2026-03-20

### Highlights

- Added caption animation capability metadata in `GET /v1/editor/capabilities`.
- Synced the SDK to the latest Indream Editor State OpenAPI contract.

### Breaking Changes

- `EditorCapabilities` now includes required `captionAnimations` (Python field: `caption_animations`).
- Editor-state payloads must follow the latest schema shape for animated numeric fields (for example `{ "value": number, "keyframes": [] }` where required).
- Caption assets now require `timingGranularity` (`word` | `line`).

### Migration Guide

1. Update capability parsing logic to consume `capabilities.caption_animations.in_`, `out`, and `loop`.
2. If you construct editor-state JSON manually, migrate numeric geometry/motion fields to the schema-defined animated track shape.
3. Ensure caption assets include `timingGranularity` before calling `client.editor.validate(...)` or `client.exports.create(...)`.

### Notes

- OpenAPI files were refreshed from the latest official API spec.
