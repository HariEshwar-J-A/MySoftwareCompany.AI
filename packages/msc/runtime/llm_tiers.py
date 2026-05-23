# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Map org role llm_tier labels to configured model names."""

from __future__ import annotations

from typing import Any

from msc.config import LLMTierMapping, MSCConfig


def model_for_tier(tier: str, tiers: LLMTierMapping) -> str:
    mapping = {
        "economy": tiers.economy,
        "standard": tiers.standard,
        "premium": tiers.premium,
    }
    return mapping.get(tier, tiers.standard)


def tier_plan_for_roles(roles: list[Any], config: MSCConfig) -> dict[str, str]:
    """Return agent slug/path → resolved model name for workspace metadata."""
    plan: dict[str, str] = {}
    for role in roles:
        tier = getattr(role, "llm_tier", "standard")
        agent_key = getattr(role, "agency_slug", None) or getattr(role, "name", "unknown")
        plan[str(agent_key)] = model_for_tier(tier, config.llm_tiers)
    return plan


def record_tier_plan(workspace_metadata: dict[str, Any], plan: dict[str, str]) -> dict[str, Any]:
    workspace_metadata["llm_tier_plan"] = plan
    return workspace_metadata
