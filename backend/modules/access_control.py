from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any


ROLE_PERMISSIONS = {
    "owner": {"orders:read", "orders:update", "tax_settings:read", "tax_settings:update", "settings:read", "settings:update"},
    "manager": {"orders:read", "orders:update", "settings:read"},
    "staff": {"orders:read", "orders:update"},
}


def _secret() -> bytes:
    return os.environ.get("PURBLUM_BUSINESS_LOGIN_SECRET", "purblum-local-demo-secret").encode("utf-8")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def issue_token(role: str, username: str, ttl_seconds: int = 8 * 60 * 60) -> str:
    payload = {
        "role": role,
        "username": username,
        "exp": int(time.time()) + ttl_seconds,
    }
    body = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_token(token: str) -> dict[str, Any] | None:
    if not token or "." not in token:
        return None
    body, sig = token.rsplit(".", 1)
    expected = hmac.new(_secret(), body.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None
    try:
        payload = json.loads(_unb64(body).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    role = str(payload.get("role", ""))
    if role not in ROLE_PERMISSIONS:
        return None
    return payload


def authenticate(users: list[dict[str, Any]], role: str, access_code: str) -> dict[str, Any] | None:
    for user in users:
        if user.get("role") == role and hmac.compare_digest(str(user.get("access_code", "")), str(access_code)):
            return user
    return None


def permissions_for(role: str) -> set[str]:
    return set(ROLE_PERMISSIONS.get(role, set()))
