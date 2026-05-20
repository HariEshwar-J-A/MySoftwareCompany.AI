# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Phase 0 foundation checks."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vendor_licenses_exist() -> None:
    assert (ROOT / "vendor" / "MetaGPT" / "LICENSE").is_file()
    assert (ROOT / "vendor" / "agency-agents" / "LICENSE").is_file()


def test_info_sentry_absent() -> None:
    assert not (ROOT / "vendor" / "agency-agents" / "info-sentry").exists()


def test_busl_root_files() -> None:
    assert (ROOT / "LICENSE").is_file()
    assert (ROOT / "NOTICE").is_file()
    assert (ROOT / "COMMERCIAL.md").is_file()


def test_msc_version() -> None:
    from msc import __version__

    assert __version__
