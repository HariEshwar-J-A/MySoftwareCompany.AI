# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""MySoftwareCompany: thin Team wrapper for org templates and workspace layout."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from metagpt.logs import logger
from metagpt.schema import Message, UserMessage
from metagpt.team import Team

from msc.review.gate import HumanReviewGate, ReviewDecision
from msc.runtime._types import AgentSpec
from msc.runtime.agency_role import AgencyRoleZero
from msc.runtime.orchestrator import AgentsOrchestrator

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
class OrgTemplate:
    name: str
    description: str = ""
    budget_default: float = 15.0
    orchestrator: OrgOrchestratorRef | None = None
    roles: list[OrgRoleRef] = field(default_factory=list)
    human_review: OrgHumanReviewConfig | None = None


def workspace_dir_for_org(org_name: str, workspace_root: Path | str = Path("workspace")) -> Path:
    slug = org_name.replace(" ", "-").lower()
    return Path(workspace_root) / slug


class MySoftwareCompany(Team):
    """MetaGPT Team that hires an org roster from agency agent specs."""

    org_name: str = ""
    workspace: Path = Path("workspace/default")
    org_template: OrgTemplate | None = None

    def __init__(self, *, workspace: Path | str | None = None, org_template: OrgTemplate | None = None, **data: Any):
        super().__init__(**data)
        if org_template is not None:
            self.org_template = org_template
            self.org_name = org_template.name
        if workspace is not None:
            self.workspace = Path(workspace)
        elif org_template is not None:
            self.workspace = workspace_dir_for_org(org_template.name)
        self.workspace.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_org(
        cls,
        template: OrgTemplate,
        *,
        workspace_root: Path | str = Path("workspace"),
        context: Any = None,
    ) -> MySoftwareCompany:
        workspace = workspace_dir_for_org(template.name, workspace_root)
        return cls(workspace=workspace, org_template=template, context=context)

    def hire_from_template(self, template: OrgTemplate, load_spec: LoadSpecFn) -> None:
        """Hire TeamLeader + agency roles declared in an org YAML template."""
        self.org_template = template
        self.org_name = template.name
        self.workspace = workspace_dir_for_org(template.name, self.workspace.parent)
        self.workspace.mkdir(parents=True, exist_ok=True)

        roster: list[Any] = []
        orch_ref = template.orchestrator
        if orch_ref is None:
            raise ValueError(f"Org '{template.name}' has no orchestrator block")

        orch_spec = load_spec(orch_ref.agent)
        if orch_ref.metagpt_class.lower() in ("teamleader", "team_leader", "orchestrator"):
            roster.append(AgentsOrchestrator.from_spec(orch_spec, llm_tier="premium"))
        else:
            roster.append(AgencyRoleZero.from_spec(orch_spec, llm_tier="premium"))

        for entry in template.roles:
            spec = load_spec(entry.agent)
            roster.append(
                AgencyRoleZero.from_spec(
                    spec,
                    tools=entry.tools or None,
                    llm_tier=entry.llm_tier,
                )
            )

        self.hire(roster)
        logger.info("Hired %s roles for org '%s' into %s", len(roster), template.name, self.workspace)

    def bootstrap(self, template: OrgTemplate, idea: str, *, load_spec: LoadSpecFn) -> None:
        """Hire roster, set budget, and publish the project idea."""
        self.hire_from_template(template, load_spec)
        self.invest(template.budget_default)
        self.run_project(idea)

    def write_org_metadata(self, extra: dict[str, Any] | None = None) -> Path:
        meta_path = self.workspace / ".msc" / "org.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "org": self.org_name,
            "workspace": str(self.workspace),
            "budget_default": self.org_template.budget_default if self.org_template else None,
        }
        if extra:
            payload.update(extra)
        meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return meta_path

    async def run_with_review(
        self,
        idea: str = "",
        *,
        n_round: int = 20,
        load_spec: LoadSpecFn | None = None,
        no_human_review: bool = False,
        review_stages: Sequence[str] | None = None,
        interactive_review: bool = True,
    ) -> list[Message]:
        """Run the company, pausing at human-review checkpoints when configured."""
        template = self.org_template
        if template is None:
            raise ValueError("org_template is required; use from_org() or hire_from_template() first")

        has_roles = bool(self.env and getattr(self.env, "roles", None))
        if load_spec is not None and not has_roles:
            self.bootstrap(template, idea, load_spec=load_spec)
        elif idea:
            self.invest(template.budget_default)
            self.run_project(idea)

        review_cfg = template.human_review or OrgHumanReviewConfig()
        gate = HumanReviewGate(self.workspace, required=review_cfg.required)
        gate.apply_bypass_flag(no_human_review)
        self.write_org_metadata(gate.read_metadata())

        stages = list(review_stages or review_cfg.before or ["deliver"])
        history = await self.run(n_round=n_round, idea=idea if not self.idea else "")

        if review_cfg.required and not no_human_review and "deliver" in stages:
            decision = gate.checkpoint("deliver", interactive=interactive_review)
            if decision == ReviewDecision.REVISE:
                feedback = gate.last_feedback or "Human requested revisions before deliverable."
                self._publish_review_feedback(feedback)
                history = await self.run(n_round=min(n_round, 5))
            elif decision == ReviewDecision.REJECT:
                gate.record_run_outcome("rejected")
                logger.warning("Run rejected at human review gate for org '%s'", self.org_name)
                return history

        gate.record_run_outcome("completed")
        self.write_org_metadata(gate.read_metadata())
        return history

    def _publish_review_feedback(self, feedback: str) -> None:
        if not self.env:
            return
        self.env.publish_message(
            UserMessage(
                content=f"[Human review — REVISE]\n{feedback}",
                send_to="all",
            )
        )
