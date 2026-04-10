# Changelog

## 0.3.1 - 2026-04-10

### Added

- Added bundled editor state example fixtures for captions, caption offsets, charts, runtime snapshots, deleted assets, and text templates.
- Added strict `client.editor.validate(...)` example coverage for schema-valid and schema-invalid editor state payloads before request dispatch.

### Changed

- Updated the bundled editor state schema to cover caption offset validation, deleted asset status snapshots, text template node contracts, and expanded chart payload shapes.
- Python editor validation now ships with the latest OpenAPI example set for caption, chart, runtime, and text template payloads.

## 0.3.0 - 2026-04-04

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
