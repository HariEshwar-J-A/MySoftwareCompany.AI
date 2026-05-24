# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Ed25519-signed license tokens and local entitlement storage (~/.msc/license.json)."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from msc.config import DEFAULT_CONFIG_DIR

LICENSE_PREFIX = "MSC1"
DEFAULT_PUBLISHER_PUBKEY = (
    Path(__file__).resolve().parents[1] / "marketplace" / "publisher_pubkey.pem"
)


class LicensePayload(BaseModel):
    customer_id: str
    tier: str = "marketplace"
    entitled_packs: list[str] = Field(default_factory=list)
    expires_at: str | None = None  # ISO-8601 UTC

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expiry


def entitlement_path() -> Path:
    return DEFAULT_CONFIG_DIR / "license.json"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


def issue_license_token(
    payload: LicensePayload,
    *,
    private_key_pem: bytes,
) -> str:
    """Sign a license token (admin / gen_license_key.py)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 private key PEM")
    body = _b64url_encode(json.dumps(payload.model_dump(), separators=(",", ":")).encode())
    sig = _b64url_encode(key.sign(body.encode()))
    return f"{LICENSE_PREFIX}.{body}.{sig}"


def verify_license_token(
    token: str,
    *,
    public_key_pem: bytes | None = None,
) -> LicensePayload:
    """Verify signature and parse payload. Raises ValueError on failure."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    parts = token.strip().split(".")
    if len(parts) != 3 or parts[0] != LICENSE_PREFIX:
        raise ValueError("Invalid license token format (expected MSC1.<payload>.<sig>)")
    _, body, sig_b64 = parts
    pem = public_key_pem if public_key_pem is not None else DEFAULT_PUBLISHER_PUBKEY.read_bytes()
    key = serialization.load_pem_public_key(pem)
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("Expected Ed25519 public key PEM")
    key.verify(_b64url_decode(sig_b64), body.encode())
    payload = LicensePayload.model_validate(json.loads(_b64url_decode(body)))
    if payload.is_expired():
        raise ValueError("License token expired")
    return payload


def save_stored_license(token: str, payload: LicensePayload | None = None) -> Path:
    path = entitlement_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {"token": token.strip()}
    if payload is not None:
        data["payload"] = payload.model_dump()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def load_stored_license() -> tuple[str, LicensePayload] | None:
    path = entitlement_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    token = str(data.get("token", "")).strip()
    if not token:
        return None
    return token, verify_license_token(token)
