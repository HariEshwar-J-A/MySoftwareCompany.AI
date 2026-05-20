# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Index vendor/agency-agents personas (excludes info-sentry)."""

from __future__ import annotations

from pathlib import Path

from msc.loader.agent_spec import AgentSpec
from msc.loader.markdown_parser import parse_agent_file, parse_agent_markdown

_DEFAULT_AGENTS_ROOT = Path("vendor/agency-agents")
_EXCLUDED_PARTS = frozenset({"info-sentry"})


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_agents_root() -> Path:
    return repo_root() / _DEFAULT_AGENTS_ROOT


def catalog_root(agents_root: Path | str | None = None) -> Path:
    if agents_root is None:
        return default_agents_root()
    path = Path(agents_root)
    if path.is_absolute():
        return path
    return repo_root() / path


def is_excluded_path(path: Path) -> bool:
    return bool(_EXCLUDED_PARTS.intersection(path.parts))


def iter_agent_paths(agents_root: Path | str | None = None) -> list[Path]:
    root = catalog_root(agents_root)
    if not root.is_dir():
        return []
    paths: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        if path.name.startswith("."):
            continue
        if is_excluded_path(path):
            continue
        paths.append(path)
    return paths


def list_agents(
    division: str | None = None,
    *,
    agents_root: Path | str | None = None,
) -> list[AgentSpec]:
    """Return all parsed agent specs, optionally filtered by division."""
    root = catalog_root(agents_root)
    specs: list[AgentSpec] = []
    for path in iter_agent_paths(root):
        spec = parse_agent_file(path, agents_root=root)
        if division and spec.division != division:
            continue
        specs.append(spec)
    return sorted(specs, key=lambda item: (item.division, item.slug))


def get_agent(slug: str, *, agents_root: Path | str | None = None) -> AgentSpec | None:
    """Look up an agent by slug (filename stem)."""
    root = catalog_root(agents_root)
    if not root.is_dir():
        return None

    exact = [p for p in root.rglob(f"{slug}.md") if not is_excluded_path(p)]
    if exact:
        return parse_agent_file(exact[0], agents_root=root)

    suffix_matches = [
        p
        for p in iter_agent_paths(root)
        if p.stem == slug or p.stem.endswith(f"-{slug}")
    ]
    if len(suffix_matches) == 1:
        return parse_agent_file(suffix_matches[0], agents_root=root)
    if len(suffix_matches) > 1:
        for path in suffix_matches:
            if path.stem == slug:
                return parse_agent_file(path, agents_root=root)
    return None


def list_divisions(*, agents_root: Path | str | None = None) -> list[str]:
    return sorted({spec.division for spec in list_agents(agents_root=agents_root)})


def load_agent_markdown(
    text: str,
    *,
    path: Path | str,
    agents_root: Path | str | None = None,
) -> AgentSpec:
    """Parse markdown text (used by tests and tooling)."""
    root = catalog_root(agents_root) if agents_root else Path(path).parent
    return parse_agent_markdown(text, path=path, agents_root=root)
