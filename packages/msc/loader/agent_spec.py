# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Pydantic model for agency-agents persona markdown."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AgentSpec(BaseModel):
    """Parsed agency-agents persona suitable for RoleZero instruction assembly."""

    name: str
    slug: str
    division: str
    description: str
    vibe: str = ""
    path: str
    identity: str = ""
    core_mission: str = ""
    critical_rules: list[str] = Field(default_factory=list)
    deliverables: str = ""
    workflow: str = ""
    communication_style: str = ""
    success_metrics: str = ""
    raw_instruction: str = ""
    color: str = ""
    emoji: str = ""
