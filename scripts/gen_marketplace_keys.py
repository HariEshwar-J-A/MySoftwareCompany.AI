#!/usr/bin/env python3
# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1
"""Generate Ed25519 publisher keypair for marketplace signing (dev / CI setup)."""

from __future__ import annotations

import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_KEY_PATH = ROOT / "scripts" / ".marketplace_dev_key.pem"
PUBLIC_KEY_PATH = ROOT / "packages" / "msc" / "marketplace" / "publisher_pubkey.pem"


def generate_keypair(*, force: bool = False) -> tuple[Path, Path]:
    if PRIVATE_KEY_PATH.exists() and not force:
        raise SystemExit(
            f"Private key already exists: {PRIVATE_KEY_PATH} (use --force to overwrite)"
        )

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

    PRIVATE_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRIVATE_KEY_PATH.write_bytes(private_pem)
    PUBLIC_KEY_PATH.write_bytes(public_pem)
    return PRIVATE_KEY_PATH, PUBLIC_KEY_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate marketplace Ed25519 publisher keys.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing private key")
    args = parser.parse_args()
    private_path, public_path = generate_keypair(force=args.force)
    print(f"Wrote private key: {private_path}")
    print(f"Wrote public key:  {public_path}")


if __name__ == "__main__":
    main()
