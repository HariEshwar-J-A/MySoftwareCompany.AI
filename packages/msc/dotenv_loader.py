# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Load repository-root `.env` into the process environment (does not override existing vars)."""

from __future__ import annotations

import os
from pathlib import Path

_REPO_MARKERS = (Path("packages") / "msc", Path("pyproject.toml"))


def find_repo_root(start: Path | None = None) -> Path | None:
    """Return MySoftwareCompany.AI repo root, or None if not inside the project."""
    if explicit := os.environ.get("MSC_REPO_ROOT", "").strip():
        root = Path(explicit).expanduser().resolve()
        return root if root.is_dir() else None

    current = (start or Path.cwd()).resolve()
    for directory in (current, *current.parents):
        if (directory / _REPO_MARKERS[0]).is_dir() and (directory / _REPO_MARKERS[1]).is_file():
            return directory
    return None


def load_project_dotenv(*, start: Path | None = None) -> Path | None:
    """Load `<repo>/.env` if present. Returns path to loaded file, or None."""
    root = find_repo_root(start)
    if root is None:
        return None
    env_path = root / ".env"
    if not env_path.is_file():
        return None

    try:
        from dotenv import load_dotenv
    except ImportError:
        return None

    load_dotenv(env_path, override=False)
    return env_path
