"""Loader → runtime org template bridge."""

from pathlib import Path

from msc.config import MSCConfig
from msc.loader.org_template import load_org_template
from msc.loader.runtime_bridge import make_load_spec, to_runtime_template

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_to_runtime_template_startup_mvp() -> None:
    cfg = MSCConfig(orgs_root=REPO_ROOT / "orgs")
    loader_tpl = load_org_template("startup-mvp", cfg)
    runtime_tpl = to_runtime_template(loader_tpl)
    assert runtime_tpl.name == "startup-mvp"
    assert runtime_tpl.orchestrator is not None
    assert runtime_tpl.orchestrator.agent.endswith("agents-orchestrator.md")
    assert len(runtime_tpl.roles) == 4
    assert runtime_tpl.human_review is not None
    assert runtime_tpl.human_review.required is True


def test_make_load_spec_resolves_orchestrator_path() -> None:
    if not (REPO_ROOT / "vendor/agency-agents").is_dir():
        return
    cfg = MSCConfig(agency_agents_root=REPO_ROOT / "vendor/agency-agents")
    load_spec = make_load_spec(cfg)
    spec = load_spec("vendor/agency-agents/specialized/agents-orchestrator.md")
    assert "orchestrator" in spec.slug or "agents" in spec.slug
