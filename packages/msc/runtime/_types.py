# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""AgentSpec import shim until feat/loader is merged."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from msc.loader.agent_spec import AgentSpec as AgentSpec
else:
    try:
        from msc.loader.agent_spec import AgentSpec
    except ImportError:
        from dataclasses import dataclass, field

        @dataclass
        class AgentSpec:
            name: str
            slug: str = ""
            division: str = ""
            description: str = ""
            vibe: str = ""
            path: str = ""
            identity: str = ""
            core_mission: str = ""
            critical_rules: list[str] = field(default_factory=list)
            deliverables: str = ""
            workflow: str = ""
            communication_style: str = ""
            success_metrics: str = ""
            raw_instruction: str = ""
