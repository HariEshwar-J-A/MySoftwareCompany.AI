# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Premium org-pack signing and loading."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from msc.entitlements.keys import (
    DEFAULT_PUBLISHER_PUBKEY,
    LicensePayload,
    _b64url_decode,
    _b64url_encode,
)
from msc.loader.org_template import OrgTemplate

PACK_VERSION = 1


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def publisher_private_key_path() -> Path:
    return _repo_root() / "scripts" / ".marketplace_dev_key.pem"


def premium_orgs_dir() -> Path:
    return _repo_root() / "orgs" / "premium"


def sign_org_yaml(yaml_text: str, *, pack_id: str) -> dict:
    """Create a signed pack envelope (admin / sign_org_pack.py)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    yaml_b64 = _b64url_encode(yaml_text.encode())
    envelope: dict = {"pack_id": pack_id, "version": PACK_VERSION, "yaml_b64": yaml_b64}
    body = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
    priv_path = publisher_private_key_path()
    if not priv_path.is_file():
        raise FileNotFoundError(
            f"Publisher private key not found: {priv_path}\n"
            "Run: python scripts/gen_marketplace_keys.py"
        )
    private_key = serialization.load_pem_private_key(priv_path.read_bytes(), password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Expected Ed25519 private key")
    envelope["signature"] = _b64url_encode(private_key.sign(body))
    return envelope


def verify_and_read_org_yaml(envelope: dict) -> str:
    """Verify publisher signature and return org YAML text."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    verify_body = {k: envelope[k] for k in ("pack_id", "version", "yaml_b64") if k in envelope}
    body = json.dumps(verify_body, sort_keys=True, separators=(",", ":")).encode()
    pub = serialization.load_pem_public_key(DEFAULT_PUBLISHER_PUBKEY.read_bytes())
    if not isinstance(pub, Ed25519PublicKey):
        raise ValueError("Invalid publisher public key")
    pub.verify(_b64url_decode(str(envelope["signature"])), body)
    return _b64url_decode(str(envelope["yaml_b64"])).decode()


def list_premium_pack_ids() -> list[str]:
    directory = premium_orgs_dir()
    if not directory.is_dir():
        return []
    return sorted(p.name.removesuffix(".yaml.enc") for p in directory.glob("*.yaml.enc"))


def load_premium_org_template(
    pack_id: str,
    *,
    payload: LicensePayload,
) -> OrgTemplate:
    if pack_id not in payload.entitled_packs:
        raise PermissionError(f"License does not entitle pack {pack_id!r}")
    path = premium_orgs_dir() / f"{pack_id}.yaml.enc"
    if not path.is_file():
        raise FileNotFoundError(f"Premium pack not found: {path}")
    envelope = json.loads(path.read_text(encoding="utf-8"))
    data = yaml.safe_load(verify_and_read_org_yaml(envelope))
    template = OrgTemplate.model_validate(data)
    return template.model_copy(update={"pack_id": pack_id, "license": "premium"})
