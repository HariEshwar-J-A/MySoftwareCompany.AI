# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""NEXUS phase state machine — tracks org phase progression in workspace metadata."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from msc.runtime.org_model import OrgPhaseRef, OrgTemplate

NEXUS_STATE_FILE = ".msc/nexus.json"


@dataclass
class NexusState:
    org: str
    mode: str
    phases: list[dict[str, Any]]
    current_phase_index: int = 0
    status: str = "in_progress"

    @property
    def current_phase(self) -> dict[str, Any] | None:
        if not self.phases or self.current_phase_index >= len(self.phases):
            return None
        return self.phases[self.current_phase_index]

    def to_dict(self) -> dict[str, Any]:
        return {
            "org": self.org,
            "mode": self.mode,
            "phases": self.phases,
            "current_phase_index": self.current_phase_index,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NexusState:
        return cls(
            org=data.get("org", ""),
            mode=data.get("mode", ""),
            phases=list(data.get("phases") or []),
            current_phase_index=int(data.get("current_phase_index", 0)),
            status=data.get("status", "in_progress"),
        )


def _phase_to_dict(phase: OrgPhaseRef) -> dict[str, Any]:
    return {
        "id": phase.id,
        "playbook": phase.playbook,
        "agents": list(phase.agents),
        "parallel": phase.parallel,
        "dev_qa_loop": phase.dev_qa_loop,
    }


class NexusRunner:
    """Persist and advance NEXUS pipeline phases for an org run."""

    def __init__(self, workspace: Path | str, template: OrgTemplate):
        self.workspace = Path(workspace).expanduser().resolve()
        self.template = template
        self._path = self.workspace / NEXUS_STATE_FILE

    def load(self) -> NexusState:
        if not self._path.is_file():
            return self.initialize()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return self.initialize()
        return NexusState.from_dict(data)

    def save(self, state: NexusState) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(state.to_dict(), indent=2) + "\n", encoding="utf-8")

    def initialize(self) -> NexusState:
        phases = [_phase_to_dict(p) for p in self.template.phases]
        state = NexusState(org=self.template.name, mode=self.template.mode, phases=phases)
        self.save(state)
        return state

    def phase_brief(self, state: NexusState | None = None) -> str:
        """Context block injected into the project idea for the active phase."""
        state = state or self.load()
        phase = state.current_phase
        if phase is None:
            return ""
        agents = ", ".join(phase.get("agents") or [])
        parallel = "parallel activation" if phase.get("parallel") else "sequential activation"
        dev_qa = " with dev↔QA loop" if phase.get("dev_qa_loop") else ""
        return (
            f"[NEXUS phase: {phase.get('id', 'unknown')}]\n"
            f"Playbook: {phase.get('playbook', '')}\n"
            f"Activate agents ({parallel}{dev_qa}): {agents}\n"
        )

    def advance(self) -> NexusState:
        state = self.load()
        if state.current_phase_index + 1 < len(state.phases):
            state.current_phase_index += 1
            state.status = "in_progress"
        else:
            state.status = "complete"
        self.save(state)
        return state

    def mark_complete(self) -> NexusState:
        state = self.load()
        state.status = "complete"
        state.current_phase_index = max(len(state.phases) - 1, 0)
        self.save(state)
        return state
