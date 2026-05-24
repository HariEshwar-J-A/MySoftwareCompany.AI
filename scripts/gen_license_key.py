#!/usr/bin/env python3
# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1
"""Issue an MSC1 license token for a customer and entitled premium packs."""

from __future__ import annotations

import argparse
from pathlib import Path

from msc.entitlements.keys import LicensePayload, issue_license_token

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_KEY = ROOT / "scripts" / ".marketplace_dev_key.pem"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an MSC1 marketplace license token.")
    parser.add_argument("--customer-id", required=True, help="Customer identifier")
    parser.add_argument(
        "--pack",
        action="append",
        dest="packs",
        default=[],
        help="Entitled premium pack id (repeatable)",
    )
    parser.add_argument("--expires-at", default=None, help="Optional ISO-8601 UTC expiry")
    parser.add_argument(
        "--private-key",
        type=Path,
        default=DEFAULT_PRIVATE_KEY,
        help="Publisher private key PEM (default: scripts/.marketplace_dev_key.pem)",
    )
    args = parser.parse_args()

    if not args.private_key.is_file():
        raise SystemExit(
            f"Private key not found: {args.private_key}\n"
            "Run: python scripts/gen_marketplace_keys.py"
        )

    payload = LicensePayload(
        customer_id=args.customer_id,
        entitled_packs=args.packs,
        expires_at=args.expires_at,
    )
    token = issue_license_token(payload, private_key_pem=args.private_key.read_bytes())
    print(token)


if __name__ == "__main__":
    main()
