# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Detect whether LLM credentials are configured for MetaGPT runs."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

_PLACEHOLDER_KEYS = frozenset({"", "YOUR_API_KEY", "sk-xxx", "xxx"})

LLM_ENV_KEYS = (
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "METAGPT_API_KEY",
    "OPENROUTER_API_KEY",
)

_METAGPT_CONFIG_HINT = (
    "Add your API key to ~/.metagpt/config2.yaml (see vendor/MetaGPT/config/config2.example.yaml). "
    "Keys are never stored in this repository."
)


def _key_from_metagpt_yaml() -> str:
    path = Path.home() / ".metagpt" / "config2.yaml"
    if not path.is_file():
        return ""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return ""
    llm = data.get("llm") if isinstance(data, dict) else None
    if not isinstance(llm, dict):
        return ""
    return str(llm.get("api_key") or "").strip()


def llm_credentials_ready() -> tuple[bool, str]:
    """Return (ready, user-facing hint when not ready)."""
    if any(os.environ.get(k, "").strip() for k in LLM_ENV_KEYS):
        return True, ""

    key = _key_from_metagpt_yaml()
    if key and key not in _PLACEHOLDER_KEYS:
        return True, ""

    return False, _METAGPT_CONFIG_HINT
