# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

from msc.config import (
    LLMTierMapping,
    OPENROUTER_MODEL_ECONOMY,
    OPENROUTER_MODEL_PREMIUM,
    OPENROUTER_MODEL_STANDARD,
)
from msc.llm_openrouter import llm_override_updates, openrouter_configured


def test_default_tier_models() -> None:
    tiers = LLMTierMapping()
    assert tiers.economy == OPENROUTER_MODEL_ECONOMY
    assert tiers.standard == OPENROUTER_MODEL_STANDARD
    assert tiers.premium == OPENROUTER_MODEL_PREMIUM
    assert OPENROUTER_MODEL_ECONOMY == "deepseek/deepseek-v4-flash:free"
    assert OPENROUTER_MODEL_PREMIUM == "moonshotai/kimi-k2.6"


def test_openrouter_override_when_key_set(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.delenv("MSC_LLM_API_TYPE", raising=False)
    assert openrouter_configured()

    class FakeLlm:
        api_key = "old"

    updates = llm_override_updates("moonshotai/kimi-k2.6", FakeLlm())
    assert updates["api_type"] == "openrouter"
    assert updates["model"] == "moonshotai/kimi-k2.6"
    assert updates["api_key"] == "sk-or-test"


def test_model_only_override_without_openrouter(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("MSC_LLM_API_TYPE", raising=False)
    assert not openrouter_configured()
    assert llm_override_updates("gpt-4o", object()) == {"model": "gpt-4o"}
