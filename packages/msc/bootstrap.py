# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Generate local config files from repo templates and `.env` (setup automation)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from msc.config import (
    OPENROUTER_MODEL_ECONOMY,
    OPENROUTER_MODEL_PREMIUM,
    OPENROUTER_MODEL_STANDARD,
    LLMTierMapping,
    MSCConfig,
)
from msc.dotenv_loader import find_repo_root, load_project_dotenv

_PLACEHOLDER_KEYS = frozenset({"", "YOUR_API_KEY", "YOUR_OPENROUTER_API_KEY", "sk-xxx", "xxx"})


def repo_root(start: Path | None = None) -> Path:
    root = find_repo_root(start or Path(__file__).resolve().parents[2])
    if root is None:
        raise RuntimeError("Not inside a MySoftwareCompany.AI repository.")
    return root


def ensure_env_file(root: Path, *, force: bool = False) -> tuple[Path, bool]:
    """Create `.env` from `.env.example`. Returns (path, created)."""
    env_path = root / ".env"
    example = root / ".env.example"
    if env_path.exists() and not force:
        return env_path, False
    if not example.is_file():
        raise FileNotFoundError(f"Missing template: {example}")
    shutil.copy(example, env_path)
    return env_path, True


def write_msc_user_config(root: Path, *, force: bool = False) -> tuple[Path, bool]:
    """Write `~/.msc/config.yaml` with absolute repo paths."""
    from msc.config import DEFAULT_CONFIG_PATH

    path = DEFAULT_CONFIG_PATH
    if path.exists() and not force:
        return path, False

    cfg = MSCConfig(
        workspace_root=root / "workspace",
        orgs_root=root / "orgs",
        agency_agents_root=root / "vendor" / "agency-agents",
        llm_api_type="openrouter",
        default_org="startup-mvp",
        default_budget=15.0,
        default_rounds=20,
        llm_tiers=LLMTierMapping(
            economy=OPENROUTER_MODEL_ECONOMY,
            standard=OPENROUTER_MODEL_STANDARD,
            premium=OPENROUTER_MODEL_PREMIUM,
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(cfg.model_dump_yaml(), handle, default_flow_style=False, sort_keys=False)
    return path, True


def _read_openrouter_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def _metagpt_config_path() -> Path:
    return Path.home() / ".metagpt" / "config2.yaml"


def _metagpt_template_data(root: Path) -> dict:
    template_path = root / "config" / "metagpt.openrouter.example.yaml"
    if not template_path.is_file():
        raise FileNotFoundError(f"Missing template: {template_path}")
    raw = template_path.read_text(encoding="utf-8")
    lines = [line for line in raw.splitlines() if not line.lstrip().startswith("#")]
    return yaml.safe_load("\n".join(lines)) or {}


def sync_metagpt_api_key_from_env() -> tuple[Path, bool]:
    """Patch api_key in existing ~/.metagpt/config2.yaml when OPENROUTER_API_KEY is set."""
    path = _metagpt_config_path()
    key = _read_openrouter_key()
    if not path.is_file() or not key or key in _PLACEHOLDER_KEYS:
        return path, False
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    llm = data.setdefault("llm", {})
    if llm.get("api_key") == key:
        return path, False
    llm["api_key"] = key
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, default_flow_style=False, sort_keys=False)
    return path, True


def write_metagpt_config(root: Path, *, force: bool = False) -> tuple[Path, bool]:
    """Write `~/.metagpt/config2.yaml` for OpenRouter from template + `.env` key."""
    path = _metagpt_config_path()
    if path.exists() and not force:
        synced, updated = sync_metagpt_api_key_from_env()
        return synced, updated

    data = _metagpt_template_data(root)
    llm = data.setdefault("llm", {})
    key = _read_openrouter_key()
    llm["api_key"] = key if key and key not in _PLACEHOLDER_KEYS else "YOUR_OPENROUTER_API_KEY"

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, default_flow_style=False, sort_keys=False)
    return path, True


def ensure_workspace(root: Path) -> Path:
    workspace = root / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def ensure_marketplace_dev_keys(root: Path) -> tuple[Path | None, bool]:
    """Generate publisher keys if missing (for local marketplace / website checkout)."""
    private_key = root / "scripts" / ".marketplace_dev_key.pem"
    public_key = root / "packages" / "msc" / "marketplace" / "publisher_pubkey.pem"
    if private_key.is_file() and public_key.is_file():
        return private_key, False
    script = root / "scripts" / "gen_marketplace_keys.py"
    if not script.is_file():
        return None, False
    subprocess.run([sys.executable, str(script)], cwd=root, check=True)
    return private_key, True


def install_website_deps(root: Path) -> bool:
    """Run `npm ci` in website/ when Node is available."""
    website = root / "website"
    if not (website / "package.json").is_file():
        return False
    if not shutil.which("npm"):
        return False
    subprocess.run(["npm", "ci"], cwd=website, check=True)
    return True


def validate_env_for_run() -> list[str]:
    """Return list of blocking issues before `msc run`."""
    issues: list[str] = []
    key = _read_openrouter_key()
    if not key or key in _PLACEHOLDER_KEYS:
        issues.append("Set OPENROUTER_API_KEY in the repo-root .env file.")
    metagpt_path = Path.home() / ".metagpt" / "config2.yaml"
    if not metagpt_path.is_file():
        issues.append(f"Missing MetaGPT config: {metagpt_path} (run: msc init)")
    return issues


def run_init(
    *,
    root: Path | None = None,
    force: bool = False,
    env_only: bool = False,
    full: bool = False,
) -> dict[str, str]:
    """Bootstrap local config from repo `.env` (used by `msc init`)."""
    repo = root or repo_root()
    lines: dict[str, str] = {}

    if env_only:
        env_path = repo / ".env"
        if not env_path.is_file():
            env_path, created = ensure_env_file(repo, force=False)
            lines["env"] = f"{'Created' if created else 'Exists'}: {env_path}"
        load_project_dotenv(start=repo)
        mg_path, synced = sync_metagpt_api_key_from_env()
        if synced:
            lines["metagpt_key"] = f"Synced OPENROUTER_API_KEY → {mg_path}"
        else:
            lines["metagpt_key"] = "No change (set OPENROUTER_API_KEY in .env first)"
        key = _read_openrouter_key()
        lines["openrouter"] = (
            "OPENROUTER_API_KEY is set" if key and key not in _PLACEHOLDER_KEYS else "TODO: set OPENROUTER_API_KEY in .env"
        )
        return lines

    return run_bootstrap(
        root=repo,
        force=force,
        skip_vendor=not full,
        skip_website=not full,
        skip_marketplace_keys=False,
    )


def run_bootstrap(
    *,
    root: Path | None = None,
    force: bool = False,
    skip_vendor: bool = False,
    skip_website: bool = False,
    skip_marketplace_keys: bool = False,
) -> dict[str, str]:
    """Generate configs and directories. Returns human-readable status lines."""
    repo = root or repo_root()
    lines: dict[str, str] = {}

    env_path, env_new = ensure_env_file(repo, force=force)
    lines["env"] = f"{'Created' if env_new else 'Exists'}: {env_path}"
    load_project_dotenv(start=repo)

    msc_path, msc_new = write_msc_user_config(repo, force=force)
    lines["msc"] = f"{'Created' if msc_new else 'Exists'}: {msc_path}"

    mg_path, mg_new = write_metagpt_config(repo, force=force)
    action = "Updated" if mg_new else "Exists"
    lines["metagpt"] = f"{action}: {mg_path}"
    synced_path, synced = sync_metagpt_api_key_from_env()
    if synced:
        lines["metagpt_key"] = f"Synced OPENROUTER_API_KEY → {synced_path}"

    ws = ensure_workspace(repo)
    lines["workspace"] = f"Ready: {ws}"

    if not skip_marketplace_keys:
        mk_path, mk_new = ensure_marketplace_dev_keys(repo)
        if mk_path:
            lines["marketplace_keys"] = f"{'Created' if mk_new else 'Exists'}: {mk_path}"

    if not skip_vendor and (repo / "scripts" / "vendor_sync.sh").is_file():
        subprocess.run(["bash", str(repo / "scripts" / "vendor_sync.sh")], cwd=repo, check=True)
        lines["vendor"] = "Synced vendor/MetaGPT and vendor/agency-agents"

    if not skip_website:
        try:
            if install_website_deps(repo):
                lines["website"] = "Installed npm dependencies in website/"
            else:
                lines["website"] = "Skipped website npm (no Node or package.json)"
        except subprocess.CalledProcessError as exc:
            lines["website"] = f"Warning: website npm ci failed ({exc})"

    key = _read_openrouter_key()
    if key and key not in _PLACEHOLDER_KEYS:
        lines["openrouter"] = "OPENROUTER_API_KEY is set"
    else:
        lines["openrouter"] = "TODO: set OPENROUTER_API_KEY in .env"

    return lines
