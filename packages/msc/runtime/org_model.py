# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Runtime org template dataclasses (no MetaGPT import)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from msc.loader.agent_spec import AgentSpec

LoadSpecFn = Callable[[str], AgentSpec]


@dataclass
class OrgOrchestratorRef:
    agent: str
    metagpt_class: str = "TeamLeader"


@dataclass
class OrgRoleRef:
    agent: str
    tools: list[str] = field(default_factory=list)
    llm_tier: str = "standard"
    role: str | None = None


@dataclass
class OrgHumanReviewConfig:
    required: bool = True
    before: list[str] = field(default_factory=lambda: ["deliver"])


@dataclass
class OrgPhaseRef:
    id: str
    playbook: str
    agents: list[str] = field(default_factory=list)
    parallel: bool = False
    dev_qa_loop: bool = False


@dataclass
class OrgGatesConfig:
    max_retries: int = 3
    require_evidence: bool = True
    phase_advance: str = "reality_checker_pass"


@dataclass
class OrgTemplate:
    name: str
    description: str = ""
    mode: str = ""
    budget_default: float = 15.0
    orchestrator: OrgOrchestratorRef | None = None
    roles: list[OrgRoleRef] = field(default_factory=list)
    phases: list[OrgPhaseRef] = field(default_factory=list)
    gates: OrgGatesConfig | None = None
    human_review: OrgHumanReviewConfig | None = None


def resolve_workspace_root(workspace_root: Path | str) -> Path:
    """Expand and absolutize workspace root (prevents nested relative paths)."""
    return Path(workspace_root).expanduser().resolve()


def workspace_dir_for_org(org_name: str, workspace_root: Path | str = Path("workspace")) -> Path:
    slug = org_name.replace(" ", "-").lower()
    return resolve_workspace_root(workspace_root) / slug
