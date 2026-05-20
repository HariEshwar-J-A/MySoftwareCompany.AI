#!/usr/bin/env python3
# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1
"""Enforce BUSL file headers in BUSL-covered paths (CI)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HEADER_LINES = (
    "# Copyright (c) 2026 MySoftwareCompany.AI",
    "# SPDX-License-Identifier: BUSL-1.1",
)

SCAN_ROOTS = (
    ROOT / "packages" / "msc",
    ROOT / "scripts",
    ROOT / "tests",
    ROOT / "benchmarks",
    ROOT / "orgs",
    ROOT / "website",
)

EXTENSIONS = {".py", ".sh"}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_ROOTS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in EXTENSIONS:
                if path.name == "license_header.py":
                    continue
                files.append(path)
    return sorted(files)


def _content_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if lines and lines[0].startswith("#!"):
        return lines[1:]
    return lines


def has_header(text: str) -> bool:
    lines = _content_lines(text)
    if len(lines) < len(HEADER_LINES):
        return False
    return lines[: len(HEADER_LINES)] == list(HEADER_LINES)


def apply_header(text: str) -> str:
    lines = text.splitlines()
    shebang = ""
    body_lines = lines
    if lines and lines[0].startswith("#!"):
        shebang = lines[0] + "\n"
        body_lines = lines[1:]
    body = "\n".join(body_lines)
    if has_header(text):
        content = _content_lines(text)
        body = "\n".join(content[len(HEADER_LINES) :]).lstrip("\n")
    header = "\n".join(HEADER_LINES) + "\n\n"
    return shebang + header + body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit 1 if any file lacks the header")
    parser.add_argument("--fix", action="store_true", help="Add missing headers")
    args = parser.parse_args()

    missing: list[Path] = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8")
        if has_header(text):
            continue
        if args.fix:
            path.write_text(apply_header(text), encoding="utf-8")
        else:
            missing.append(path)

    if missing and args.check:
        for path in missing:
            rel = path.relative_to(ROOT)
            print(f"missing BUSL header: {rel}", file=sys.stderr)
        return 1

    if args.fix and not args.check:
        print(f"fixed {len(missing)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
