from __future__ import annotations

import hmac
import time
from collections.abc import Mapping
from hashlib import sha256

INDREAM_WEBHOOK_TIMESTAMP_HEADER = "x-indream-timestamp"
INDREAM_WEBHOOK_SIGNATURE_HEADER = "x-indream-signature"
DEFAULT_WEBHOOK_MAX_SKEW_SECONDS = 300


def _resolve_header_value(headers: Mapping[str, object], target_key: str) -> str | None:
    lower_key = target_key.lower()
    for key, value in headers.items():
        if key.lower() != lower_key:
            continue
        if isinstance(value, list | tuple):
            value = value[0] if value else None
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except UnicodeDecodeError:
                return None
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None
    return None


def verify_export_webhook_signature(
    *,
    webhook_secret: str,
    timestamp: str,
    raw_body: str,
    signature: str,
) -> bool:
    if not webhook_secret or not timestamp or not signature:
        return False

    normalized_signature = signature.strip().lower()
    if len(normalized_signature) != 64:
        return False
    if any(ch not in "0123456789abcdef" for ch in normalized_signature):
        return False

    payload = f"{timestamp}.{raw_body}".encode()
    expected = hmac.new(webhook_secret.encode(), payload, sha256).hexdigest()
    return hmac.compare_digest(expected, normalized_signature)


def verify_export_webhook_request(
    *,
    webhook_secret: str,
    raw_body: str,
    headers: Mapping[str, object],
    max_skew_seconds: int = DEFAULT_WEBHOOK_MAX_SKEW_SECONDS,
    now_timestamp_seconds: int | None = None,
) -> bool:
    timestamp = _resolve_header_value(headers, INDREAM_WEBHOOK_TIMESTAMP_HEADER)
    signature = _resolve_header_value(headers, INDREAM_WEBHOOK_SIGNATURE_HEADER)
    if timestamp is None or signature is None:
        return False

    if not timestamp.isdigit():
        return False
    timestamp_seconds = int(timestamp)

    if max_skew_seconds < 0:
        return False
    current_timestamp = int(time.time()) if now_timestamp_seconds is None else now_timestamp_seconds
    if current_timestamp < 0:
        return False

    # Enforce a bounded timestamp window to reduce replay risk.
    if abs(current_timestamp - timestamp_seconds) > max_skew_seconds:
        return False

    return verify_export_webhook_signature(
        webhook_secret=webhook_secret,
        timestamp=timestamp,
        raw_body=raw_body,
        signature=signature,
    )
