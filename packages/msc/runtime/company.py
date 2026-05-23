# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""MySoftwareCompany: thin Team wrapper for org templates and workspace layout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from metagpt.logs import logger
from metagpt.schema import Message, UserMessage
from metagpt.team import Team

from msc.review.deliverable import DeliverableCheckError
from msc.review.quality_gates import run_deliverable_gate
from msc.review.gate import HumanReviewGate, ReviewDecision
from msc.runtime.agency_role import AgencyRoleZero
from msc.runtime.llm_tiers import model_for_tier, record_tier_plan, tier_plan_for_roles
from msc.runtime.nexus import NexusRunner
from msc.runtime.orchestrator import AgentsOrchestrator
from msc.runtime.org_model import (
    LoadSpecFn,
    OrgGatesConfig,
    OrgHumanReviewConfig,
    OrgOrchestratorRef,
    OrgPhaseRef,
    OrgRoleRef,
    OrgTemplate,
    workspace_dir_for_org,
)
from msc.runtime.serialize import save_team


class MySoftwareCompany(Team):
    """MetaGPT Team that hires an org roster from agency agent specs."""

    org_name: str = ""
    workspace: Path = Path("workspace/default")
    org_template: OrgTemplate | None = None
    msc_config: Any = None

    def __init__(
        self,
        *,
        workspace: Path | str | None = None,
        org_template: OrgTemplate | None = None,
        msc_config: Any = None,
        **data: Any,
    ):
        super().__init__(**data)
        self.msc_config = msc_config
        if org_template is not None:
            self.org_template = org_template
            self.org_name = org_template.name
        if workspace is not None:
            self.workspace = Path(workspace).expanduser().resolve()
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
        msc_config: Any = None,
    ) -> MySoftwareCompany:
        workspace = workspace_dir_for_org(template.name, workspace_root)
        return cls(workspace=workspace, org_template=template, context=context, msc_config=msc_config)

    def _bind_roster_workspace(self, roster: list[Any]) -> None:
        for role in roster:
            if hasattr(role, "bind_workspace"):
                role.bind_workspace(self.workspace)

    def hire_from_template(self, template: OrgTemplate, load_spec: LoadSpecFn) -> None:
        """Hire TeamLeader + agency roles declared in an org YAML template."""
        self.org_template = template
        self.org_name = template.name
        self.workspace = self.workspace.resolve()
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

        self._bind_roster_workspace(roster)
        self.hire(roster)
        self._apply_llm_tiers()
        if self.msc_config is not None and self.env:
            tier_plan = tier_plan_for_roles(list(self.env.roles.values()), self.msc_config)
            meta_path = self.workspace / ".msc" / "org.json"
            if meta_path.exists():
                extra = json.loads(meta_path.read_text(encoding="utf-8"))
            else:
                extra = {}
            record_tier_plan(extra, tier_plan)
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            meta_path.write_text(json.dumps(extra, indent=2) + "\n", encoding="utf-8")
        logger.info("Hired {} roles for org '{}' into {}", len(roster), template.name, self.workspace)

    def _apply_llm_tiers(self) -> None:
        """Assign per-role MetaGPT private_config so each role uses its llm_tier model."""
        if self.msc_config is None or not self.env:
            return
        try:
            from metagpt.config2 import Config as MetaGPTConfig  # noqa: PLC0415
        except ImportError:
            return
        for role in self.env.roles.values():
            tier = getattr(role, "llm_tier", "standard")
            if tier == "standard":
                continue
            model_name = model_for_tier(tier, self.msc_config.llm_tiers)
            try:
                base_cfg: MetaGPTConfig = role.context.config
                overridden_llm = base_cfg.llm.model_copy(update={"model": model_name})
                private_cfg = base_cfg.model_copy(update={"llm": overridden_llm})
                role.set_config(private_cfg)
                logger.debug("Role '{}' → llm_tier={} model={}", role.name, tier, model_name)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not apply llm_tier for role '{}': {}", role.name, exc)

    def _nexus_idea(self, idea: str) -> str:
        if not self.org_template or not self.org_template.phases:
            return idea
        nexus = NexusRunner(self.workspace, self.org_template)
        brief = nexus.phase_brief()
        return f"{brief}\n{idea}" if brief else idea

    def bootstrap(self, template: OrgTemplate, idea: str, *, load_spec: LoadSpecFn) -> None:
        """Hire roster, set budget, and publish the project idea."""
        self.hire_from_template(template, load_spec)
        self.invest(template.budget_default)
        self.run_project(self._nexus_idea(idea))

    def write_org_metadata(self, extra: dict[str, Any] | None = None) -> Path:
        meta_path = self.workspace / ".msc" / "org.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "org": self.org_name,
            "workspace": str(self.workspace.resolve()),
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
            self.run_project(self._nexus_idea(idea))

        if template.phases:
            NexusRunner(self.workspace, template).initialize()

        review_cfg = template.human_review or OrgHumanReviewConfig()
        gates_cfg = template.gates or OrgGatesConfig()
        gate = HumanReviewGate(self.workspace, required=review_cfg.required)
        gate.apply_bypass_flag(no_human_review)
        self.write_org_metadata(gate.read_metadata())

        stages = list(review_stages or review_cfg.before or ["deliver"])
        if template.phases:
            history = await self._run_phases(template.phases, gates_cfg, n_round)
        else:
            try:
                history = await self.run(n_round=n_round, idea=idea if not self.idea else "")
            except Exception as exc:  # noqa: BLE001
                logger.warning("Team run raised an exception — continuing to gate checks: {}", exc)
                history = []

        if review_cfg.required and not no_human_review and "deliver" in stages:
            decision = gate.checkpoint("deliver", interactive=interactive_review)
            if decision == ReviewDecision.REVISE:
                feedback = gate.last_feedback or "Human requested revisions before deliverable."
                self._publish_review_feedback(feedback)
                history = await self.run(n_round=min(n_round, 5))
            elif decision == ReviewDecision.REJECT:
                gate.record_run_outcome("rejected", no_human_review=no_human_review)
                logger.warning("Run rejected at human review gate for org '{}'", self.org_name)
                return history

        deliverable = await run_deliverable_gate(self, gates_cfg)
        gate.write_metadata({"quality_gate": deliverable.to_dict()})
        if not deliverable.passed:
            gate.record_run_outcome("failed_deliverable_check", no_human_review=no_human_review)
            for msg in deliverable.report.errors:
                logger.error("Deliverable check: {}", msg)
            raise DeliverableCheckError(deliverable.report)

        if template.phases:
            NexusRunner(self.workspace, template).mark_complete()

        gate.record_run_outcome("completed", no_human_review=no_human_review)
        self.write_org_metadata(gate.read_metadata())
        try:
            save_team(self, self.workspace)
        except Exception as exc:  # noqa: BLE001 — serialization optional
            logger.warning("Team serialize skipped: {}", exc)
        return history

    async def _run_phases(
        self,
        phases: list[OrgPhaseRef],
        gates_cfg: OrgGatesConfig,
        total_rounds: int,
    ) -> list[Message]:
        """Execute each NEXUS phase as its own MetaGPT sub-run.

        Rounds are divided evenly across phases. Between phases, a brief
        deliverable check is done; failures are surfaced as feedback but do
        not abort early (the final gate in run_with_review handles that).
        """
        history: list[Message] = []
        nexus = NexusRunner(self.workspace, self.org_template)  # type: ignore[arg-type]
        rounds_per_phase = max(1, total_rounds // len(phases))

        for i, phase in enumerate(phases):
            # Advance state and broadcast the phase context to all agents.
            state = nexus.advance() if i > 0 else nexus.initialize()
            brief = nexus.phase_brief(state)
            logger.info(
                "NEXUS phase {}/{}: {} ({}r)",
                i + 1,
                len(phases),
                phase.id,
                rounds_per_phase,
            )
            if brief:
                self._publish_review_feedback(
                    f"[NEXUS → {phase.id}]\n{brief}"
                )

            # Run the phase. If the env goes idle quickly (TeamLeader called `end`
            # but the engineer hasn't written files yet), re-nudge and run again.
            try:
                phase_history = await self.run(n_round=rounds_per_phase)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Phase '{}' run raised: {}", phase.id, exc)
                phase_history = None
            if phase_history:
                history.extend(phase_history)

            # If workspace is still empty after the first sub-run, nudge the team
            # and run more rounds so the engineer has a real chance to write files.
            from msc.review.deliverable import verify_workspace_deliverables  # noqa: PLC0415
            check = verify_workspace_deliverables(self.workspace)
            if not check.ok:
                logger.info("Phase '{}' workspace empty after first pass — nudging team for {} more rounds", phase.id, rounds_per_phase)
                self._publish_review_feedback(
                    f"[Phase {phase.id} — write deliverables now]\n"
                    "No source files found yet. Engineer: please write all required files to the workspace immediately."
                )
                try:
                    extra = await self.run(n_round=rounds_per_phase)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Phase '{}' nudge run raised: {}", phase.id, exc)
                    extra = None
                if extra:
                    history.extend(extra)

            # Mid-phase gate: check evidence, feed back errors as revision request.
            if i < len(phases) - 1 and gates_cfg.require_evidence:
                from msc.review.deliverable import verify_workspace_deliverables  # noqa: PLC0415

                report = verify_workspace_deliverables(self.workspace)
                if not report.ok:
                    logger.warning(
                        "Phase '{}' gate not fully passed — continuing to next phase with feedback",
                        phase.id,
                    )
                    self._publish_review_feedback(
                        "[Phase gate — incomplete evidence]\n"
                        + "\n".join(f"- {e}" for e in report.errors)
                    )

        nexus.mark_complete()
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
