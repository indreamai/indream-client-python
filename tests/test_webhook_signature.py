from indream.webhooks import verify_export_webhook_request, verify_export_webhook_signature

WEBHOOK_SECRET = "whs_indream_test_secret"
RAW_BODY = (
    '{"eventType":"EXPORT_COMPLETED","task":{"taskId":"638ad4d9-51e5-42ec-bb50-0db761bba304"}}'
)
TIMESTAMP = "1710307200"
VALID_SIGNATURE = "0967e30ab5a11ccd298ad131166419d2384b54f38390e6ab52db71a01ad6161a"


def test_verify_export_webhook_signature_accepts_valid_signature() -> None:
    valid = verify_export_webhook_signature(
        webhook_secret=WEBHOOK_SECRET,
        timestamp=TIMESTAMP,
        raw_body=RAW_BODY,
        signature=VALID_SIGNATURE,
    )

    assert valid is True


def test_verify_export_webhook_signature_rejects_invalid_signature() -> None:
    valid = verify_export_webhook_signature(
        webhook_secret=WEBHOOK_SECRET,
        timestamp=TIMESTAMP,
        raw_body=RAW_BODY,
        signature="0" * 64,
    )

    assert valid is False


def test_verify_export_webhook_request_accepts_valid_headers() -> None:
    valid = verify_export_webhook_request(
        webhook_secret=WEBHOOK_SECRET,
        raw_body=RAW_BODY,
        headers={
            "X-Indream-Timestamp": TIMESTAMP,
            "X-Indream-Signature": VALID_SIGNATURE,
        },
        now_timestamp_seconds=int(TIMESTAMP),
        max_skew_seconds=300,
    )

    assert valid is True


def test_verify_export_webhook_request_rejects_missing_headers() -> None:
    valid = verify_export_webhook_request(
        webhook_secret=WEBHOOK_SECRET,
        raw_body=RAW_BODY,
        headers={},
        now_timestamp_seconds=int(TIMESTAMP),
    )

    assert valid is False


def test_verify_export_webhook_request_rejects_skewed_timestamp() -> None:
    valid = verify_export_webhook_request(
        webhook_secret=WEBHOOK_SECRET,
        raw_body=RAW_BODY,
        headers={
            "x-indream-timestamp": TIMESTAMP,
            "x-indream-signature": VALID_SIGNATURE,
        },
        now_timestamp_seconds=int(TIMESTAMP) + 301,
        max_skew_seconds=300,
    )

    assert valid is False
