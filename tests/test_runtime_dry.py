"""Dry-run validation without LLM calls."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from msc.config import MSCConfig
from msc.runtime.dry_run import run_dry_run

REPO_ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


@pytest.fixture
def config() -> MSCConfig:
    return MSCConfig(orgs_root=REPO_ROOT / "orgs")


@pytest.mark.parametrize("org_name", ["startup-mvp", "nexus-micro", "marketing-campaign", "incident-response"])
def test_dry_run_all_orgs(config: MSCConfig, org_name: str) -> None:
    report = run_dry_run(org_name, config)
    assert report.org == org_name
    assert report.roles_count >= 3
    assert report.phases_count >= 1


def test_dry_run_reports_missing_vendor_paths(config: MSCConfig) -> None:
    report = run_dry_run("startup-mvp", config)
    assert report.org == "startup-mvp"
    assert report.roles_count == 4
    assert report.phases_count == 2
    if not (REPO_ROOT / "vendor/agency-agents").is_dir():
        assert report.ok is False
        assert len(report.missing_paths) > 0


def test_dry_run_ok_when_paths_exist(config: MSCConfig, tmp_path: Path) -> None:
    from msc.loader.org_template import (
        GatesSpec,
        HumanReviewSpec,
        OrchestratorSpec,
        OrgTemplate,
        PhaseSpec,
        RoleSpec,
    )

    template = OrgTemplate(
        name="fixture-org",
        description="test",
        source_runbook=str(tmp_path / "runbook.md"),
        mode="test",
        orchestrator=OrchestratorSpec(agent=str(tmp_path / "orch.md")),
        roles=[RoleSpec(agent=str(tmp_path / "role.md"))],
        phases=[PhaseSpec(id="p1", playbook=str(tmp_path / "phase.md"), agents=["a"])],
        gates=GatesSpec(),
        human_review=HumanReviewSpec(),
    )
    with patch("msc.runtime.dry_run.load_org_template", return_value=template):
        with patch.object(Path, "exists", return_value=True):
            report = run_dry_run("startup-mvp", config)
    assert report.ok is True
    assert report.missing_paths == []


def test_cli_dry_run_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MSC_ORGS_ROOT", str(REPO_ROOT / "orgs"))
    from msc.cli import app

    result = runner.invoke(app, ["dry-run", "--org", "startup-mvp"])
    assert result.exit_code in (0, 1)
    assert "startup-mvp" in result.stdout
    assert "Roles:" in result.stdout


def test_cli_init_writes_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from msc import config as config_module
    from msc.cli import app

    cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config_module, "DEFAULT_CONFIG_PATH", cfg_file)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert cfg_file.exists()


def test_cli_orgs_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MSC_ORGS_ROOT", str(REPO_ROOT / "orgs"))
    from msc.cli import app

    result = runner.invoke(app, ["orgs", "list"])
    assert result.exit_code == 0
    assert "startup-mvp" in result.stdout
    assert "nexus-micro" in result.stdout
