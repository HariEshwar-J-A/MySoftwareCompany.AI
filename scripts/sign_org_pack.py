#!/usr/bin/env python3
# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1
"""Sign a premium org YAML into orgs/premium/<pack_id>.yaml.enc."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from msc.marketplace.loader import premium_orgs_dir, sign_org_yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sign a premium org pack envelope.")
    parser.add_argument("pack_id", help="Premium pack id (output filename stem)")
    parser.add_argument(
        "yaml_path",
        type=Path,
        nargs="?",
        help="Source org YAML (default: orgs/premium/<pack_id>.yaml)",
    )
    args = parser.parse_args()

    yaml_path = args.yaml_path or (premium_orgs_dir() / f"{args.pack_id}.yaml")
    if not yaml_path.is_file():
        raise SystemExit(f"Source YAML not found: {yaml_path}")

    envelope = sign_org_yaml(yaml_path.read_text(encoding="utf-8"), pack_id=args.pack_id)
    out_dir = premium_orgs_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.pack_id}.yaml.enc"
    out_path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote signed pack: {out_path}")


if __name__ == "__main__":
    main()
