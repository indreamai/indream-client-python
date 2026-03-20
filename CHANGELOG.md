# Changelog

All notable changes to `indream-client` are documented in this file.

## 0.2.0 - 2026-03-20

### Highlights

- Synced the SDK to the latest Indream Editor State OpenAPI contract.
- Added local `editorState` schema checks before `client.editor.validate(...)` and `client.exports.create(...)`.
- Added caption animation capability metadata from `GET /v1/editor/capabilities`.

### Breaking Changes

- `EditorCapabilities` now includes required `captionAnimations` (Python field: `caption_animations`).
- Invalid `editorState` now raises `ValidationError` before network dispatch in `client.editor.validate(...)` and `client.exports.create(...)`.
- Caption assets now require `timingGranularity` (`word` | `line`).

### Migration Guide

1. Update capability parsing logic to consume `capabilities.caption_animations.in_`, `out`, and `loop`.
2. Ensure your `editorState` payload matches the latest schema before calling `client.editor.validate(...)` or `client.exports.create(...)`.
3. Ensure caption assets include `timingGranularity` (`word` or `line`).

### Notes

- OpenAPI files were refreshed from the latest official API spec.
