"""Org template YAML schema tests."""

from pathlib import Path

import pytest

from msc.config import MSCConfig
from msc.loader.org_template import OrgTemplate, load_org_template

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config() -> MSCConfig:
    return MSCConfig(orgs_root=REPO_ROOT / "orgs")


def test_startup_mvp_loads(config: MSCConfig) -> None:
    template = load_org_template("startup-mvp", config)
    assert template.name == "startup-mvp"
    assert template.mode == "nexus-sprint"
    assert template.license == "oss"
    assert template.budget_default == 15.0


def test_startup_mvp_orchestrator_and_roles(config: MSCConfig) -> None:
    template = load_org_template("startup-mvp", config)
    assert template.orchestrator.metagpt_class == "TeamLeader"
    assert "agents-orchestrator" in template.orchestrator.agent
    assert len(template.roles) == 4
    tiers = {role.llm_tier for role in template.roles}
    assert tiers == {"economy", "standard", "premium"}


def test_startup_mvp_phases_and_gates(config: MSCConfig) -> None:
    template = load_org_template("startup-mvp", config)
    assert [phase.id for phase in template.phases] == ["discovery", "build"]
    assert template.phases[0].parallel is True
    assert template.phases[1].dev_qa_loop is True
    assert template.gates.max_retries == 3
    assert template.human_review.required is True


def test_org_template_referenced_paths(config: MSCConfig) -> None:
    template = load_org_template("startup-mvp", config)
    paths = template.referenced_paths()
    assert any("scenario-startup-mvp" in path for path in paths)
    assert any("frontend-developer" in path for path in paths)
    assert len(paths) >= 6


def test_org_template_round_trip_schema(config: MSCConfig) -> None:
    template = load_org_template("startup-mvp", config)
    reloaded = OrgTemplate.model_validate(template.model_dump())
    assert reloaded.model_dump() == template.model_dump()
