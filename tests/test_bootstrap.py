# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

from pathlib import Path

import yaml
from msc.bootstrap import ensure_env_file, ensure_workspace, write_msc_user_config


def test_ensure_env_and_msc_config(tmp_path: Path) -> None:
    (tmp_path / "packages" / "msc").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text("[project]\nname='mscai'\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("FOO=bar\n", encoding="utf-8")
    (tmp_path / "orgs").mkdir()
    (tmp_path / "vendor" / "agency-agents").mkdir(parents=True)

    env_path, created = ensure_env_file(tmp_path)
    assert created
    assert env_path.read_text() == "FOO=bar\n"

    msc_home = tmp_path / "msc_home"
    msc_path = msc_home / "config.yaml"
    import msc.config as msc_config

    original = msc_config.DEFAULT_CONFIG_PATH
    try:
        msc_config.DEFAULT_CONFIG_PATH = msc_path
        out, wrote = write_msc_user_config(tmp_path, force=True)
        assert wrote
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert "deepseek/deepseek-v4-flash:free" in data["llm_tiers"]["economy"]
        assert str(tmp_path / "workspace") in data["workspace_root"]
    finally:
        msc_config.DEFAULT_CONFIG_PATH = original

    ws = ensure_workspace(tmp_path)
    assert ws.is_dir()
