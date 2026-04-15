# Changelog

## 1.0.0 - 2026-04-15

### Added

- Initial public release of the Python SDK for Indream OpenAPI.
- Added typed sync and async clients for `exports`, `editor`, `projects`, `uploads`, `assets`, and `illustrations`.
- Added support for one-off exports, export task retrieval, export task listing, and polling until completion.
- Added support for persistent project workflows, including project creation, listing, retrieval, metadata updates, editor-state sync, deletion, asset binding, asset unbinding, and project-based exports.
- Added direct upload support for image, video, and audio files through `/v1/uploads`, with typed asset models that include the public media fields returned by the API.
- Added asset retrieval and deletion helpers for uploaded files managed through `/v1/assets`.
- Added editor capability retrieval, illustration search, and editor-state validation helpers.
- Added local `editorState` schema validation before `editor.validate(...)`, `projects.create(...)`, `projects.sync(...)`, and `exports.create(...)` requests are sent.
- Added automatic retry handling for retryable API and transport failures.
- Added support for Python 3.10+.
