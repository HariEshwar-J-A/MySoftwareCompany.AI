"""Phase 3: NEXUS state, quality gates, LLM tiers, resume helpers."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from msc.config import LLMTierMapping, MSCConfig
from msc.loader.org_template import load_org_template
from msc.loader.runtime_bridge import to_runtime_template
from msc.review.deliverable import verify_workspace_deliverables
from msc.review.quality_gates import run_deliverable_gate
from msc.runtime.llm_tiers import model_for_tier, tier_plan_for_roles
from msc.runtime.nexus import NexusRunner, NexusState
from msc.runtime.org_model import OrgGatesConfig, OrgPhaseRef, OrgTemplate
from msc.runtime.serialize import has_saved_team, team_storage_path

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config() -> MSCConfig:
    return MSCConfig(orgs_root=REPO_ROOT / "orgs")


def test_nexus_initialize_and_advance(tmp_path: Path) -> None:
    template = OrgTemplate(
        name="test-org",
        mode="nexus-micro",
        phases=[
            OrgPhaseRef(id="a", playbook="p1.md", agents=["agent-a"]),
            OrgPhaseRef(id="b", playbook="p2.md", agents=["agent-b"], dev_qa_loop=True),
        ],
    )
    runner = NexusRunner(tmp_path, template)
    state = runner.initialize()
    assert state.current_phase_index == 0
    assert state.current_phase["id"] == "a"
    assert state.status == "in_progress"

    brief = runner.phase_brief(state)
    assert "[NEXUS phase: a]" in brief
    assert "agent-a" in brief

    advanced = runner.advance()
    assert advanced.current_phase_index == 1
    assert advanced.current_phase["id"] == "b"
    assert "dev↔QA loop" in runner.phase_brief(advanced)

    complete = runner.mark_complete()
    assert complete.status == "complete"


def test_nexus_state_round_trip() -> None:
    state = NexusState(
        org="x",
        mode="nexus-sprint",
        phases=[{"id": "p1", "playbook": "pb", "agents": ["a"]}],
        current_phase_index=0,
    )
    reloaded = NexusState.from_dict(state.to_dict())
    assert reloaded.org == state.org
    assert reloaded.phases == state.phases


def test_model_for_tier_mapping() -> None:
    tiers = LLMTierMapping(economy="cheap", standard="mid", premium="best")
    assert model_for_tier("economy", tiers) == "cheap"
    assert model_for_tier("unknown", tiers) == "mid"


def test_tier_plan_for_roles() -> None:
    role = MagicMock(agency_slug="frontend-dev", llm_tier="premium")
    cfg = MSCConfig(llm_tiers=LLMTierMapping(premium="claude-opus"))
    plan = tier_plan_for_roles([role], cfg)
    assert plan["frontend-dev"] == "claude-opus"


def test_deliverable_gate_passes_valid_html(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        "<html><body><script>document.body.textContent='ok';</script></body></html>",
        encoding="utf-8",
    )
    company = MagicMock()
    company.workspace = tmp_path

    async def _run() -> None:
        result = await run_deliverable_gate(company, OrgGatesConfig(max_retries=0))
        assert result.passed is True
        assert result.attempts == 1

    asyncio.run(_run())


def test_deliverable_gate_retries_on_failure(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(
        "<html><script>const x = <div/>;</script></html>",
        encoding="utf-8",
    )
    company = MagicMock()
    company.workspace = tmp_path
    company.run = AsyncMock()
    company._publish_review_feedback = MagicMock()

    async def fix_on_retry(*_args, **_kwargs) -> None:
        (tmp_path / "index.html").write_text(
            "<html><script>document.body.textContent='fixed';</script></html>",
            encoding="utf-8",
        )

    company.run.side_effect = fix_on_retry

    async def _run() -> None:
        result = await run_deliverable_gate(
            company,
            OrgGatesConfig(max_retries=2),
            extra_rounds_per_retry=1,
        )
        assert result.passed is True
        assert result.retries_used == 1
        company.run.assert_awaited_once()

    asyncio.run(_run())


def test_deliverable_gate_skipped_when_evidence_not_required(tmp_path: Path) -> None:
    report = verify_workspace_deliverables(tmp_path)
    assert report.ok is False


def test_deliverable_gate_skip_evidence(tmp_path: Path) -> None:
    company = MagicMock()
    company.workspace = tmp_path

    async def _run() -> None:
        result = await run_deliverable_gate(
            company,
            OrgGatesConfig(require_evidence=False),
        )
        assert result.passed is True
        assert result.attempts == 0

    asyncio.run(_run())


def test_team_storage_helpers(tmp_path: Path) -> None:
    path = team_storage_path(tmp_path)
    assert path == tmp_path.resolve() / ".msc" / "team"
    assert has_saved_team(tmp_path) is False
    path.mkdir(parents=True)
    (path / "team.json").write_text("{}", encoding="utf-8")
    assert has_saved_team(tmp_path) is True


@pytest.mark.parametrize(
    "org_name,min_roles,min_phases",
    [
        ("startup-mvp", 4, 2),
        ("nexus-micro", 3, 1),
        ("marketing-campaign", 5, 2),
        ("incident-response", 5, 2),
    ],
)
def test_phase3_orgs_load(config: MSCConfig, org_name: str, min_roles: int, min_phases: int) -> None:
    template = load_org_template(org_name, config)
    runtime = to_runtime_template(template)
    assert runtime.name == org_name
    assert len(runtime.roles) >= min_roles
    assert len(runtime.phases) >= min_phases
    assert runtime.gates is not None
    assert runtime.gates.max_retries == 3
