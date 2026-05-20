from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from msc.config import MSCConfig
from msc.loader.org_template import load_org_template


class DryRunReport(BaseModel):
    org: str
    ok: bool
    roles_count: int
    phases_count: int
    missing_paths: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def run_dry_run(org_name: str, config: MSCConfig | None = None) -> DryRunReport:
    cfg = config or MSCConfig.load()
    template = load_org_template(org_name, cfg)
    root = _repo_root()
    missing = [ref for ref in template.referenced_paths() if not (root / ref).exists()]
    warnings: list[str] = []
    agents = cfg.agency_agents_root if cfg.agency_agents_root.is_absolute() else root / cfg.agency_agents_root
    if not agents.exists():
        warnings.append(f"agency_agents_root not found ({cfg.agency_agents_root}); run make vendor-sync")
    notes = ["Dry-run validates org YAML and referenced paths only (no LLM calls)."]
    try:
        import metagpt  # noqa: F401
        notes.append("MetaGPT import OK — use `msc run` for full execution (requires API keys).")
    except ImportError:
        notes.append("MetaGPT not installed — run: make install-dev")
    return DryRunReport(
        org=template.name,
        ok=not missing,
        roles_count=len(template.roles),
        phases_count=len(template.phases),
        missing_paths=missing,
        warnings=warnings,
        notes=notes,
    )


def format_report(report: DryRunReport) -> str:
    lines = [f"Org: {report.org}", f"Roles: {report.roles_count}  Phases: {report.phases_count}",
             f"Status: {'OK' if report.ok else 'MISSING PATHS'}"]
    if report.missing_paths:
        lines += ["Missing:", *[f"  - {p}" for p in report.missing_paths]]
    if report.warnings:
        lines += ["Warnings:", *[f"  - {w}" for w in report.warnings]]
    lines += report.notes
    return "\n".join(lines)
