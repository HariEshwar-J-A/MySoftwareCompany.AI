# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Phase 4: marketplace licenses, signed premium packs, and CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from msc.cli import app
from msc.entitlements.keys import (
    LicensePayload,
    entitlement_path,
    issue_license_token,
    load_stored_license,
    save_stored_license,
    verify_license_token,
)
from msc.entitlements.stripe_webhook import (
    issue_and_store_from_stripe_stub,
    stripe_checkout_to_license,
)
from msc.loader.org_template import list_org_templates, load_org_template
from msc.marketplace.loader import list_premium_pack_ids, load_premium_org_template, sign_org_yaml
from typer.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


@pytest.fixture
def publisher_keys(tmp_path: Path) -> tuple[bytes, bytes]:
    private_key = Ed25519PrivateKey.generate()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    pub_path = tmp_path / "publisher_pubkey.pem"
    pub_path.write_bytes(public_pem)
    priv_path = tmp_path / "dev_key.pem"
    priv_path.write_bytes(private_pem)
    return private_pem, public_pem


@pytest.fixture
def licensed_env(
    tmp_path: Path,
    publisher_keys: tuple[bytes, bytes],
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, LicensePayload]:
    private_pem, public_pem = publisher_keys
    pub_path = tmp_path / "publisher_pubkey.pem"
    pub_path.write_bytes(public_pem)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_PUBLISHER_PUBKEY", pub_path)
    monkeypatch.setattr("msc.marketplace.loader.DEFAULT_PUBLISHER_PUBKEY", pub_path)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_CONFIG_DIR", tmp_path / ".msc")
    monkeypatch.setattr(
        "msc.entitlements.keys.entitlement_path", lambda: tmp_path / ".msc" / "license.json"
    )

    premium_dir = tmp_path / "orgs" / "premium"
    premium_dir.mkdir(parents=True)
    yaml_text = (REPO_ROOT / "orgs" / "premium" / "fintech-studio.yaml").read_text(encoding="utf-8")
    priv_path = tmp_path / "dev_key.pem"
    priv_path.write_bytes(private_pem)
    monkeypatch.setattr("msc.marketplace.loader.publisher_private_key_path", lambda: priv_path)
    monkeypatch.setattr("msc.marketplace.loader.premium_orgs_dir", lambda: premium_dir)

    envelope = sign_org_yaml(yaml_text, pack_id="fintech-studio")
    (premium_dir / "fintech-studio.yaml.enc").write_text(
        json.dumps(envelope) + "\n", encoding="utf-8"
    )

    payload = LicensePayload(customer_id="cust_test", entitled_packs=["fintech-studio"])
    token = issue_license_token(payload, private_key_pem=private_pem)
    save_stored_license(token, payload)
    return token, payload


def test_verify_license_token_round_trip(
    publisher_keys: tuple[bytes, bytes], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    private_pem, public_pem = publisher_keys
    pub_path = tmp_path / "publisher_pubkey.pem"
    pub_path.write_bytes(public_pem)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_PUBLISHER_PUBKEY", pub_path)

    payload = LicensePayload(customer_id="cust_1", entitled_packs=["fintech-studio"])
    token = issue_license_token(payload, private_key_pem=private_pem)
    verified = verify_license_token(token, public_key_pem=public_pem)
    assert verified.customer_id == "cust_1"
    assert verified.entitled_packs == ["fintech-studio"]


def test_expired_license_rejected(publisher_keys: tuple[bytes, bytes]) -> None:
    private_pem, public_pem = publisher_keys
    payload = LicensePayload(
        customer_id="cust_1",
        entitled_packs=["fintech-studio"],
        expires_at="2020-01-01T00:00:00Z",
    )
    token = issue_license_token(payload, private_key_pem=private_pem)
    with pytest.raises(ValueError, match="expired"):
        verify_license_token(token, public_key_pem=public_pem)


def test_load_premium_org_template(licensed_env: tuple[str, LicensePayload]) -> None:
    _, payload = licensed_env
    template = load_premium_org_template("fintech-studio", payload=payload)
    assert template.name == "fintech-studio"
    assert template.license == "premium"
    assert template.pack_id == "fintech-studio"


def test_load_premium_without_entitlement(licensed_env: tuple[str, LicensePayload]) -> None:
    _, payload = licensed_env
    other = payload.model_copy(update={"entitled_packs": ["other-pack"]})
    with pytest.raises(PermissionError, match="does not entitle"):
        load_premium_org_template("fintech-studio", payload=other)


def test_load_org_template_premium_when_licensed(
    licensed_env: tuple[str, LicensePayload],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from msc.config import MSCConfig

    cfg = MSCConfig(orgs_root=REPO_ROOT / "orgs")
    template = load_org_template("fintech-studio", cfg)
    assert template.license == "premium"


def test_list_org_templates_includes_premium_when_licensed(
    licensed_env: tuple[str, LicensePayload],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from msc.config import MSCConfig

    cfg = MSCConfig(orgs_root=REPO_ROOT / "orgs")
    names = [t.name for t in list_org_templates(cfg)]
    assert "fintech-studio" in names
    assert "startup-mvp" in names


def test_stripe_stub_issues_license(
    publisher_keys: tuple[bytes, bytes],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_pem, public_pem = publisher_keys
    pub_path = tmp_path / "publisher_pubkey.pem"
    pub_path.write_bytes(public_pem)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_PUBLISHER_PUBKEY", pub_path)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_CONFIG_DIR", tmp_path / ".msc")
    monkeypatch.setattr(
        "msc.entitlements.keys.entitlement_path", lambda: tmp_path / ".msc" / "license.json"
    )

    event = {"type": "checkout.session.completed"}
    token = issue_and_store_from_stripe_stub(
        event,
        private_key_pem=private_pem,
        pack_id="fintech-studio",
        customer_id="stripe_cust_1",
    )
    assert token.startswith("MSC1.")
    stored = load_stored_license()
    assert stored is not None
    _, payload = stored
    assert payload.entitled_packs == ["fintech-studio"]


def test_stripe_stub_rejects_unknown_event(publisher_keys: tuple[bytes, bytes]) -> None:
    private_pem, _ = publisher_keys
    with pytest.raises(ValueError, match="Unsupported Stripe event"):
        stripe_checkout_to_license(
            {"type": "invoice.paid"},
            private_key_pem=private_pem,
            pack_id="fintech-studio",
            customer_id="x",
        )


def test_marketplace_login_cli(
    publisher_keys: tuple[bytes, bytes], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    private_pem, public_pem = publisher_keys
    pub_path = tmp_path / "publisher_pubkey.pem"
    pub_path.write_bytes(public_pem)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_PUBLISHER_PUBKEY", pub_path)
    monkeypatch.setattr("msc.entitlements.keys.DEFAULT_CONFIG_DIR", tmp_path / ".msc")
    monkeypatch.setattr(
        "msc.entitlements.keys.entitlement_path", lambda: tmp_path / ".msc" / "license.json"
    )

    payload = LicensePayload(customer_id="cli_user", entitled_packs=["fintech-studio"])
    token = issue_license_token(payload, private_key_pem=private_pem)
    result = runner.invoke(app, ["marketplace", "login", token])
    assert result.exit_code == 0, result.output
    assert entitlement_path().is_file()


def test_marketplace_orgs_cli(licensed_env: tuple[str, LicensePayload]) -> None:
    result = runner.invoke(app, ["marketplace", "orgs"])
    assert result.exit_code == 0, result.output
    assert "fintech-studio" in result.output
    assert "entitled" in result.output


def test_reference_premium_pack_in_repo() -> None:
    enc = REPO_ROOT / "orgs" / "premium" / "fintech-studio.yaml.enc"
    assert enc.is_file(), (
        "Run scripts/gen_marketplace_keys.py && scripts/sign_org_pack.py fintech-studio"
    )
    assert "fintech-studio" in list_premium_pack_ids()
