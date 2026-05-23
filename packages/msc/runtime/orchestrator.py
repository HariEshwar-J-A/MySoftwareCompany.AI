# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""AgentsOrchestrator: TeamLeader persona from agents-orchestrator.md + NEXUS doctrine."""

from __future__ import annotations

from typing import Any, Sequence

from metagpt.const import TEAMLEADER_NAME
from metagpt.roles.di.team_leader import TeamLeader

from msc.runtime._types import AgentSpec

NEXUS_ORCHESTRATOR_DOCTRINE = """
## NEXUS pipeline doctrine (non-negotiable)

You orchestrate the full agency pipeline under NEXUS (Non-negotiable Excellence in eXecution and Shipping):

1. **Phase discipline** — Complete each phase before advancing; activate only agents needed for the current phase.
2. **Quality loops** — Task-by-task dev↔QA validation; max 3 retries per task, then escalate via ask_human.
3. **Evidence gates** — No phase advance without Evidence Collector artifacts; Reality Checker must pass before handoff.
4. **Context handoffs** — Every publish_team_message includes paths, links, stack, requirements, and constraints from upstream.
5. **Human review** — Before any client deliverable, pause for human sign-off; never bypass for paid work.

Follow the Agents Orchestrator workflow: analyze spec → plan tasks → architecture → dev/QA loop → integration.
Coordinate specialists; do not assign consecutive micro-tasks to the same member—use aggregated instructions.
""".strip()

ORCHESTRATOR_TOOLS: list[str] = ["Plan", "RoleZero", "TeamLeader"]


class AgentsOrchestrator(TeamLeader):
    """TeamLeader with agency orchestrator persona and NEXUS routing rules."""

    profile: str = "Agents Orchestrator"
    agency_slug: str = "agents-orchestrator"
    llm_tier: str = "premium"

    @classmethod
    def from_spec(
        cls,
        spec: AgentSpec,
        *,
        tools: Sequence[str] | None = None,
        llm_tier: str = "premium",
        **kwargs: Any,
    ) -> AgentsOrchestrator:
        """Instantiate the team leader from agents-orchestrator (or compatible) spec."""
        base_instruction = getattr(spec, "raw_instruction", "") or ""
        instruction = f"{NEXUS_ORCHESTRATOR_DOCTRINE}\n\n---\n\n{base_instruction}".strip()
        tool_list = list(tools) if tools is not None else list(ORCHESTRATOR_TOOLS)
        rules = getattr(spec, "critical_rules", None) or []
        constraints = "\n".join(f"- {rule}" for rule in rules) if rules else ""
        goal = getattr(spec, "core_mission", "") or getattr(spec, "description", "")
        return cls(
            name=TEAMLEADER_NAME,
            profile=getattr(spec, "division", "") or cls.profile,
            goal=goal.strip() or "Orchestrate the agency pipeline to ship quality software",
            constraints=constraints,
            instruction=instruction,
            tools=tool_list,
            agency_slug=getattr(spec, "slug", "") or "agents-orchestrator",
            llm_tier=llm_tier,
            **kwargs,
        )
