import pytest
from pydantic import ValidationError

from indream.types import ExportWebhookEvent


def test_webhook_payload_accepts_event_envelope() -> None:
    payload = {
        "eventType": "EXPORT_COMPLETED",
        "occurredAt": "2026-03-11T13:00:00.000Z",
        "task": {
            "taskId": "638ad4d9-51e5-42ec-bb50-0db761bba304",
            "projectId": "93fb8aa8-c301-441d-bb8d-ea733cd72a7e",
            "createdByApiKeyId": "36daa18d-1cfb-4828-bef4-309e27de4235",
            "clientTaskId": "client-1",
            "status": "COMPLETED",
            "progress": 100,
            "error": None,
            "outputUrl": "https://example.com/output.mp4",
            "durationSeconds": 18.4,
            "billedStandardSeconds": 32,
            "chargedCredits": "1.6",
            "callbackUrl": "https://example.com/callback",
            "createdAt": "2026-03-11T12:59:00.000Z",
            "completedAt": "2026-03-11T13:00:00.000Z",
        },
    }

    event = ExportWebhookEvent.model_validate(payload)

    assert event.event_type == "EXPORT_COMPLETED"
    assert event.task.task_id == "638ad4d9-51e5-42ec-bb50-0db761bba304"
    assert event.task.project_id == "93fb8aa8-c301-441d-bb8d-ea733cd72a7e"
    assert event.task.status == "COMPLETED"
    assert event.task.duration_seconds == 18.4
    assert event.task.billed_standard_seconds == 32


def test_webhook_payload_rejects_legacy_data_shape() -> None:
    legacy_payload = {
        "eventType": "EXPORT_COMPLETED",
        "occurredAt": "2026-03-11T13:00:00.000Z",
        "data": {
            "taskId": "b310d6d5-3d53-423e-8417-d0878e5bd5f5",
        },
        "meta": {},
    }

    with pytest.raises(ValidationError):
        ExportWebhookEvent.model_validate(legacy_payload)


def test_webhook_payload_rejects_lowercase_event_type() -> None:
    invalid_payload = {
        "eventType": "export_completed",
        "occurredAt": "2026-03-11T13:00:00.000Z",
        "task": {
            "taskId": "f8353d52-c938-4949-a452-376e3d1c92eb",
            "projectId": None,
            "createdByApiKeyId": None,
            "clientTaskId": None,
            "status": "COMPLETED",
            "progress": 100,
            "error": None,
            "outputUrl": None,
            "durationSeconds": 0.4,
            "billedStandardSeconds": 1,
            "chargedCredits": "0.1",
            "callbackUrl": None,
            "createdAt": "2026-03-11T12:59:00.000Z",
            "completedAt": "2026-03-11T13:00:00.000Z",
        },
    }

    with pytest.raises(ValidationError):
        ExportWebhookEvent.model_validate(invalid_payload)
