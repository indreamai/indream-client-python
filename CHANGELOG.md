# Changelog

## 0.2.1 - 2026-04-04

### Added

- Added `projects`, `uploads`, and `assets` resources.
- Added `uploads.upload(...)` for file uploads.
- Added nullable `project_id` to export creation responses, export task models, and webhook task payloads.

### Changed

- OpenAPI cloud export formats are limited to `mp4` and `webm`.
- Export models accept an additional nullable `project_id` field.

## 0.2.0 - 2026-03-20

### Added

- Added local `editorState` schema checks before `client.editor.validate(...)` and `client.exports.create(...)`.
- Added caption animation capability metadata from `GET /v1/editor/capabilities`.

### Changed

- `EditorCapabilities` includes required `captionAnimations` (Python field: `caption_animations`).
- Invalid `editorState` raises `ValidationError` before network dispatch in `client.editor.validate(...)` and `client.exports.create(...)`.
- Caption assets require `timingGranularity` (`word` | `line`).
