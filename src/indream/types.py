from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED", "PAUSED", "CANCELED"]
WebhookEventType = Literal["EXPORT_STARTED", "EXPORT_COMPLETED", "EXPORT_FAILED"]


class ExportCreateResponse(BaseModel):
    task_id: str = Field(alias="taskId")
    project_id: str | None = Field(default=None, alias="projectId")
    created_at: str = Field(alias="createdAt")
    duration_seconds: float = Field(alias="durationSeconds")
    billed_standard_seconds: int = Field(alias="billedStandardSeconds")
    charged_credits: str = Field(alias="chargedCredits")


class ExportTask(BaseModel):
    task_id: str = Field(alias="taskId")
    project_id: str | None = Field(default=None, alias="projectId")
    created_by_api_key_id: str | None = Field(alias="createdByApiKeyId")
    client_task_id: str | None = Field(alias="clientTaskId")
    status: TaskStatus
    progress: float
    error: str | None
    output_url: str | None = Field(alias="outputUrl")
    duration_seconds: float = Field(alias="durationSeconds")
    billed_standard_seconds: int = Field(alias="billedStandardSeconds")
    charged_credits: str = Field(alias="chargedCredits")
    callback_url: str | None = Field(alias="callbackUrl")
    created_at: str = Field(alias="createdAt")
    completed_at: str | None = Field(alias="completedAt")


class ExportTaskListResponse(BaseModel):
    items: list[ExportTask]
    next_page_cursor: str | None = Field(alias="nextPageCursor")


class ExportWebhookEvent(BaseModel):
    event_type: WebhookEventType = Field(alias="eventType")
    occurred_at: str = Field(alias="occurredAt")
    task: ExportTask


class CaptionAnimationPresetItem(BaseModel):
    id: str
    type: str
    label: str
    preview: str


class CaptionAnimationPresetGroups(BaseModel):
    in_: list[CaptionAnimationPresetItem] = Field(alias="in")
    out: list[CaptionAnimationPresetItem]
    loop: list[CaptionAnimationPresetItem]


class EditorCapabilities(BaseModel):
    version: str
    animations: list[str]
    caption_animations: CaptionAnimationPresetGroups = Field(alias="captionAnimations")
    transitions: list[str]
    transition_presets: list[dict[str, Any]] = Field(alias="transitionPresets")
    effects: list[str]
    effect_presets: list[dict[str, Any]] = Field(alias="effectPresets")
    filters: list[str]
    filter_presets: list[dict[str, Any]] = Field(alias="filterPresets")
    shapes: list[str]
    background_presets: dict[str, Any] = Field(alias="backgroundPresets")


class EditorValidationError(BaseModel):
    code: str
    path: str
    message: str


class EditorValidationResult(BaseModel):
    valid: bool
    errors: list[EditorValidationError]


class ProjectSummary(BaseModel):
    project_id: str = Field(alias="projectId")
    title: str
    description: str | None
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class ProjectDetail(ProjectSummary):
    editor_state: dict[str, Any] = Field(alias="editorState")
    state_version: str = Field(alias="stateVersion")


class ProjectMetadataResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    title: str
    description: str | None
    updated_at: str = Field(alias="updatedAt")


class ProjectSyncResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    state_version: str = Field(alias="stateVersion")
    updated_at: str = Field(alias="updatedAt")


class ProjectDeleteResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    deleted: bool


class ProjectListResponse(BaseModel):
    items: list[ProjectSummary]
    next_page_cursor: str | None = Field(alias="nextPageCursor")


class Asset(BaseModel):
    asset_id: str = Field(alias="assetId")
    type: str
    source: str | None
    filename: str
    mimetype: str
    size: int | None
    file_url: str = Field(alias="fileUrl")
    file_key: str = Field(alias="fileKey")
    width: float | None
    height: float | None
    duration: float | None


class AssetListResponse(BaseModel):
    items: list[Asset]
    next_page_cursor: str | None = Field(alias="nextPageCursor")


class ProjectAssetBindingResponse(BaseModel):
    project_id: str = Field(alias="projectId")
    asset_id: str = Field(alias="assetId")


class ProjectAssetDeleteResponse(ProjectAssetBindingResponse):
    deleted: bool


class AssetDeleteResponse(BaseModel):
    asset_id: str = Field(alias="assetId")
    deleted: bool
