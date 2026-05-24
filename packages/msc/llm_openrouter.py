# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""OpenRouter defaults for MSC llm_tier mapping and MetaGPT LLM overrides."""

from __future__ import annotations

import os
from typing import Any

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_TYPE = "openrouter"


def openrouter_configured(*, llm_api_type: str | None = None) -> bool:
    """True when OpenRouter should be used (env key, MSC flag, or ~/.msc llm_api_type)."""
    if (llm_api_type or os.environ.get("MSC_LLM_API_TYPE", "")).strip().lower() == "openrouter":
        return True
    return bool(os.environ.get("OPENROUTER_API_KEY", "").strip())


def openrouter_api_key(fallback: str = "") -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip() or fallback


def llm_override_updates(
    model_name: str,
    base_llm: Any,
    *,
    llm_api_type: str | None = None,
) -> dict[str, Any]:
    """Fields to merge into MetaGPT LLMConfig for a role (OpenRouter or model-only)."""
    if not openrouter_configured(llm_api_type=llm_api_type):
        return {"model": model_name}
    key = openrouter_api_key(getattr(base_llm, "api_key", "") or "")
    return {
        "model": model_name,
        "api_type": OPENROUTER_API_TYPE,
        "base_url": OPENROUTER_BASE_URL,
        "api_key": key,
    }
