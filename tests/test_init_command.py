# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import os
from pathlib import Path

import yaml

from msc.bootstrap import run_init


def test_run_init_env_only_syncs_key(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    (repo / "packages" / "msc").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[project]\nname='mscai'\n", encoding="utf-8")
    (repo / "config").mkdir()
    (repo / "config" / "metagpt.openrouter.example.yaml").write_text(
        "llm:\n  api_type: openrouter\n  api_key: PLACEHOLDER\n  model: google/gemma-4-31b-it:free\n",
        encoding="utf-8",
    )
    (repo / ".env").write_text("OPENROUTER_API_KEY=sk-or-test-key\n", encoding="utf-8")

    metagpt_dir = tmp_path / ".metagpt"
    metagpt_dir.mkdir()
    config_path = metagpt_dir / "config2.yaml"
    config_path.write_text(
        yaml.safe_dump({"llm": {"api_type": "openrouter", "api_key": "old"}}),
        encoding="utf-8",
    )

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(repo)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")

    lines = run_init(root=repo, env_only=True)
    assert "OPENROUTER_API_KEY" in lines.get("openrouter", "")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert data["llm"]["api_key"] == "sk-or-test-key"
