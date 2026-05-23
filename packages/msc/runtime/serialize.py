# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Serialize and resume MetaGPT team state under workspace/.msc/team/."""

from __future__ import annotations

from pathlib import Path

TEAM_STORAGE_DIR = ".msc/team"


def team_storage_path(workspace: Path | str) -> Path:
    return Path(workspace).expanduser().resolve() / TEAM_STORAGE_DIR


def has_saved_team(workspace: Path | str) -> bool:
    path = team_storage_path(workspace) / "team.json"
    return path.is_file()


def save_team(company, workspace: Path | str) -> Path:
    """Persist MetaGPT team state for ``msc resume``."""
    dest = team_storage_path(workspace)
    dest.mkdir(parents=True, exist_ok=True)
    company.serialize(stg_path=dest)
    return dest / "team.json"


async def resume_team(
    workspace: Path | str,
    *,
    n_round: int = 10,
    idea: str = "",
) -> "MySoftwareCompany":
    """Load a serialized team and continue execution."""
    from metagpt.context import Context

    from msc.runtime.company import MySoftwareCompany

    dest = team_storage_path(workspace)
    if not has_saved_team(workspace):
        raise FileNotFoundError(f"No saved team at {dest / 'team.json'}")

    company = MySoftwareCompany.deserialize(stg_path=dest, context=Context())
    company.workspace = Path(workspace).expanduser().resolve()
    await company.run(n_round=n_round, idea=idea)
    save_team(company, workspace)
    return company
