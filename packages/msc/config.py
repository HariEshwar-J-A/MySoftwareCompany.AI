"""User configuration at ~/.msc/config.yaml with environment variable overrides."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

DEFAULT_CONFIG_DIR = Path.home() / ".msc"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yaml"
_ENV_PREFIX = "MSC_"


class LLMTierMapping(BaseModel):
    economy: str = "gpt-4o-mini"
    standard: str = "gpt-4o"
    premium: str = "claude-opus-4-20250514"


class MSCConfig(BaseModel):
    workspace_root: Path = Field(default=Path("./workspace"))
    orgs_root: Path = Field(default=Path("orgs"))
    agency_agents_root: Path = Field(default=Path("vendor/agency-agents"))
    metagpt_config: Path | None = None
    llm_tiers: LLMTierMapping = Field(default_factory=LLMTierMapping)
    default_org: str = "startup-mvp"
    default_budget: float = 15.0
    default_rounds: int = 20

    def model_dump_yaml(self) -> dict[str, Any]:
        data = self.model_dump(mode="json")
        for key in ("workspace_root", "orgs_root", "agency_agents_root", "metagpt_config"):
            if data.get(key) is not None:
                data[key] = str(data[key])
        return data

    @classmethod
    def load(cls, path: Path | None = None) -> MSCConfig:
        config_path = path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            return cls.from_env(cls())
        with config_path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        return cls.from_env(cls.model_validate(raw))

    def save(self, path: Path | None = None) -> Path:
        config_path = path or DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with config_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.model_dump_yaml(), handle, default_flow_style=False, sort_keys=False)
        return config_path

    @classmethod
    def init(cls, path: Path | None = None) -> Path:
        config_path = path or DEFAULT_CONFIG_PATH
        if config_path.exists():
            return config_path
        return cls().save(config_path)

    @classmethod
    def from_env(cls, base: MSCConfig) -> MSCConfig:
        updates: dict[str, Any] = {}
        for suffix, field in {
            "WORKSPACE_ROOT": "workspace_root",
            "ORGS_ROOT": "orgs_root",
            "AGENCY_AGENTS_ROOT": "agency_agents_root",
            "METAGPT_CONFIG": "metagpt_config",
            "DEFAULT_ORG": "default_org",
            "DEFAULT_BUDGET": "default_budget",
            "DEFAULT_ROUNDS": "default_rounds",
        }.items():
            if f"{_ENV_PREFIX}{suffix}" in os.environ:
                val = os.environ[f"{_ENV_PREFIX}{suffix}"]
                if field == "default_budget":
                    updates[field] = float(val)
                elif field == "default_rounds":
                    updates[field] = int(val)
                elif field.endswith("_root") or field == "metagpt_config":
                    updates[field] = Path(val)
                else:
                    updates[field] = val
        tier_updates = {
            t: os.environ[f"{_ENV_PREFIX}LLM_TIER_{t.upper()}"]
            for t in ("economy", "standard", "premium")
            if f"{_ENV_PREFIX}LLM_TIER_{t.upper()}" in os.environ
        }
        if tier_updates:
            updates["llm_tiers"] = base.llm_tiers.model_copy(update=tier_updates)
        return base if not updates else base.model_copy(update=updates)
