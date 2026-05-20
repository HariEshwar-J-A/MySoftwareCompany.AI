# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Tests for packages/msc/loader (markdown parser + catalog)."""

from __future__ import annotations

from pathlib import Path

import pytest

from msc.loader import (
    catalog_root,
    get_agent,
    is_excluded_path,
    iter_agent_paths,
    list_agents,
    list_divisions,
    load_agent_markdown,
    parse_agent_file,
)
from msc.loader.catalog import repo_root

FIXTURES_ROOT = Path(__file__).parent / "fixtures" / "agents"


@pytest.fixture
def fixtures_root() -> Path:
    return FIXTURES_ROOT


def test_parse_frontmatter_and_sections(fixtures_root: Path) -> None:
    path = fixtures_root / "engineering" / "mini-ai-engineer.md"
    spec = parse_agent_file(path, agents_root=fixtures_root)

    assert spec.name == "Mini AI Engineer"
    assert spec.slug == "mini-ai-engineer"
    assert spec.division == "engineering"
    assert spec.description == "Compact fixture persona for loader tests."
    assert spec.vibe == "Tests ML pipelines without burning tokens."
    assert spec.color == "blue"
    assert spec.emoji == "🤖"
    assert "Test double" in spec.identity
    assert "toy models" in spec.core_mission.lower()
    assert any("fixture" in rule.lower() for rule in spec.critical_rules)
    assert "Parser" in spec.deliverables
    assert "Parse" in spec.workflow
    assert "concise" in spec.communication_style.lower()
    assert "loader tests pass" in spec.success_metrics


def test_critical_rules_from_mandatory_process(fixtures_root: Path) -> None:
    path = fixtures_root / "testing" / "mini-evidence-collector.md"
    spec = parse_agent_file(path, agents_root=fixtures_root)

    assert spec.slug == "mini-evidence-collector"
    assert spec.division == "testing"
    assert len(spec.critical_rules) >= 3
    assert any("playwright" in rule.lower() for rule in spec.critical_rules)


def test_raw_instruction_assembled_and_trimmed(fixtures_root: Path) -> None:
    path = fixtures_root / "engineering" / "mini-ai-engineer.md"
    spec = parse_agent_file(path, agents_root=fixtures_root)

    assert spec.raw_instruction.startswith("You are **Mini AI Engineer**")
    assert "## Identity" in spec.raw_instruction
    assert "## Critical Rules" in spec.raw_instruction
    assert len(spec.raw_instruction) <= 6003


def test_raw_instruction_trimmed_when_huge() -> None:
    body = "\n".join(
        [
            "---",
            "name: Huge Agent",
            "description: x",
            "---",
            "",
            "## 🧠 Your Identity & Memory",
            "y" * 8000,
        ]
    )
    spec = load_agent_markdown(
        body,
        path=FIXTURES_ROOT / "engineering" / "huge.md",
        agents_root=FIXTURES_ROOT,
    )
    assert spec.raw_instruction.endswith("...")
    assert len(spec.raw_instruction) <= 6003


def test_catalog_lists_fixture_agents(fixtures_root: Path) -> None:
    agents = list_agents(agents_root=fixtures_root)
    slugs = {agent.slug for agent in agents}

    assert len(agents) == 3
    assert slugs == {
        "mini-ai-engineer",
        "mini-evidence-collector",
        "mini-orchestrator",
    }


def test_catalog_filter_by_division(fixtures_root: Path) -> None:
    agents = list_agents("engineering", agents_root=fixtures_root)
    assert len(agents) == 1
    assert agents[0].slug == "mini-ai-engineer"


def test_get_agent_by_slug(fixtures_root: Path) -> None:
    by_full = get_agent("mini-orchestrator", agents_root=fixtures_root)
    assert by_full is not None
    assert by_full.name == "Mini Orchestrator"

    by_stem = get_agent("mini-ai-engineer", agents_root=fixtures_root)
    assert by_stem is not None
    assert by_stem.slug == "mini-ai-engineer"


def test_list_divisions(fixtures_root: Path) -> None:
    divisions = list_divisions(agents_root=fixtures_root)
    assert divisions == ["engineering", "specialized", "testing"]


def test_info_sentry_paths_excluded(tmp_path: Path) -> None:
    sentry_dir = tmp_path / "info-sentry"
    sentry_dir.mkdir()
    (sentry_dir / "info-sentry-agent.md").write_text(
        "---\nname: Sentry\n---\n\n## 🧠 Your Identity & Memory\nhidden\n",
        encoding="utf-8",
    )
    good = tmp_path / "engineering"
    good.mkdir()
    (good / "visible-agent.md").write_text(
        "---\nname: Visible\n---\n\n## 🧠 Your Identity & Memory\nok\n",
        encoding="utf-8",
    )

    assert is_excluded_path(sentry_dir / "info-sentry-agent.md")
    paths = iter_agent_paths(tmp_path)
    assert len(paths) == 1
    assert paths[0].name == "visible-agent.md"


@pytest.mark.skipif(
    not (repo_root() / "vendor" / "agency-agents").is_dir(),
    reason="vendor/agency-agents not present",
)
def test_vendor_catalog_non_empty() -> None:
    root = catalog_root()
    agents = list_agents(agents_root=root)
    assert len(agents) > 50
    assert all("info-sentry" not in agent.path for agent in agents)
    sample = get_agent("engineering-ai-engineer", agents_root=root)
    assert sample is not None
    assert sample.name == "AI Engineer"
    assert sample.raw_instruction
