from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from msc.config import MSCConfig


class OrchestratorSpec(BaseModel):
    agent: str
    metagpt_class: str = "TeamLeader"


class RoleSpec(BaseModel):
    agent: str
    tools: list[str] = Field(default_factory=list)
    llm_tier: Literal["economy", "standard", "premium"] = "standard"
    role: str | None = None


class PhaseSpec(BaseModel):
    id: str
    playbook: str
    agents: list[str]
    parallel: bool = False
    dev_qa_loop: bool = False


class GatesSpec(BaseModel):
    max_retries: int = 3
    require_evidence: bool = True
    phase_advance: str = "reality_checker_pass"


class HumanReviewSpec(BaseModel):
    required: bool = True
    before: list[str] = Field(default_factory=lambda: ["deliver", "phase_advance"])


class OrgTemplate(BaseModel):
    name: str
    description: str
    source_runbook: str
    mode: str
    license: Literal["oss", "premium"] = "oss"
    pack_id: str | None = None
    budget_default: float = 15.0
    orchestrator: OrchestratorSpec
    roles: list[RoleSpec]
    phases: list[PhaseSpec] = Field(default_factory=list)
    gates: GatesSpec = Field(default_factory=GatesSpec)
    human_review: HumanReviewSpec = Field(default_factory=HumanReviewSpec)

    def referenced_paths(self) -> list[str]:
        paths = [self.source_runbook, self.orchestrator.agent]
        paths.extend(r.agent for r in self.roles)
        paths.extend(p.playbook for p in self.phases)
        return paths


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def orgs_dir(config: MSCConfig | None = None) -> Path:
    cfg = config or MSCConfig.load()
    orgs = cfg.orgs_root
    return orgs if orgs.is_absolute() else _repo_root() / orgs


def load_org_template(name: str, config: MSCConfig | None = None) -> OrgTemplate:
    slug = name.removesuffix(".yaml")
    path = orgs_dir(config) / f"{slug}.yaml"
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return OrgTemplate.model_validate(data)

    from msc.entitlements.keys import load_stored_license
    from msc.marketplace.loader import list_premium_pack_ids, load_premium_org_template

    if slug in list_premium_pack_ids():
        stored = load_stored_license()
        if stored is None:
            raise PermissionError(
                f"Premium org {slug!r} requires a marketplace license. "
                "Run: msc marketplace login <key>"
            )
        _, payload = stored
        return load_premium_org_template(slug, payload=payload)

    raise FileNotFoundError(f"Org template not found: {path}")


def list_org_templates(config: MSCConfig | None = None) -> list[OrgTemplate]:
    directory = orgs_dir(config)
    templates: list[OrgTemplate] = []
    if directory.is_dir():
        templates.extend(
            load_org_template(p.stem, config) for p in sorted(directory.glob("*.yaml"))
        )

    from msc.entitlements.keys import load_stored_license
    from msc.marketplace.loader import list_premium_pack_ids, load_premium_org_template

    stored = load_stored_license()
    if stored is not None:
        _, payload = stored
        oss_names = {t.name for t in templates}
        for pack_id in list_premium_pack_ids():
            if pack_id in payload.entitled_packs and pack_id not in oss_names:
                templates.append(load_premium_org_template(pack_id, payload=payload))

    return sorted(templates, key=lambda t: t.name)
