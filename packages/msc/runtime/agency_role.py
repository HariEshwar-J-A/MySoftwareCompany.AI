# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""AgencyRoleZero: MetaGPT RoleZero wired to agency-agents AgentSpec."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from pydantic import Field

from metagpt.roles.di.role_zero import RoleZero
from metagpt.tools.libs.terminal import Terminal

from msc.runtime._types import AgentSpec

DEFAULT_TOOLS: list[str] = ["Plan", "RoleZero", "Editor", "Terminal"]


def _format_constraints(spec: AgentSpec) -> str:
    rules = getattr(spec, "critical_rules", None) or []
    if not rules:
        return ""
    return "\n".join(f"- {rule}" for rule in rules)


def _goal_from_spec(spec: AgentSpec) -> str:
    mission = getattr(spec, "core_mission", "") or ""
    if mission.strip():
        return mission.strip()
    return (getattr(spec, "description", "") or spec.name).strip()


class AgencyRoleZero(RoleZero):
    """RoleZero subclass whose persona comes from an agency-agents markdown spec."""

    agency_slug: str = ""
    llm_tier: str = "standard"
    agent_path: str = ""
    terminal: Terminal = Field(default_factory=Terminal, exclude=True)

    def _update_tool_execution(self) -> None:
        super()._update_tool_execution()
        self.tool_execution_map.update(
            {
                "Terminal.run_command": self.terminal.run_command,
            }
        )

    def bind_workspace(self, workspace: str | Path) -> None:
        """Point editor/terminal at the org workspace before execution."""
        root = str(Path(workspace).resolve())
        self.editor._set_workdir(root)

    @classmethod
    def from_spec(
        cls,
        spec: AgentSpec,
        *,
        tools: Sequence[str] | None = None,
        llm_tier: str = "standard",
        **kwargs: Any,
    ) -> AgencyRoleZero:
        """Build a RoleZero from a parsed AgentSpec."""
        tool_list = list(tools) if tools is not None else list(DEFAULT_TOOLS)
        instruction = getattr(spec, "raw_instruction", "") or ""
        return cls(
            name=spec.name,
            profile=getattr(spec, "division", "") or "Agency Agent",
            goal=_goal_from_spec(spec),
            constraints=_format_constraints(spec),
            instruction=instruction,
            tools=tool_list,
            agency_slug=getattr(spec, "slug", "") or "",
            llm_tier=llm_tier,
            agent_path=getattr(spec, "path", "") or "",
            **kwargs,
        )
