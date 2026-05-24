# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import os
from pathlib import Path

from msc.dotenv_loader import find_repo_root, load_project_dotenv


def test_find_repo_root_from_cwd() -> None:
    root = find_repo_root(Path(__file__).resolve().parents[1])
    assert root is not None
    assert (root / "packages" / "msc").is_dir()


def test_load_project_dotenv_does_not_override_existing(monkeypatch, tmp_path: Path) -> None:
    fake_root = tmp_path / "proj"
    (fake_root / "packages" / "msc").mkdir(parents=True)
    (fake_root / "pyproject.toml").write_text("[project]\nname='mscai'\n", encoding="utf-8")
    (fake_root / ".env").write_text("MSC_DEFAULT_ORG=from-dotenv\n", encoding="utf-8")

    monkeypatch.chdir(fake_root)
    monkeypatch.delenv("MSC_REPO_ROOT", raising=False)
    monkeypatch.setenv("MSC_DEFAULT_ORG", "from-shell")

    loaded = load_project_dotenv(start=fake_root)
    assert loaded == fake_root / ".env"
    assert os.environ.get("MSC_DEFAULT_ORG") == "from-shell"
