# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field


STANDARD_SUITE_IDS = (
    "todo-cli",
    "static-landing",
    "fastapi-crud",
    "react-spa-auth",
    "cli-game-2048",
    "csv-transform",
)


class BenchmarkSpec(BaseModel):
    id: str
    name: str
    description: str
    idea: str
    org: str = "startup-mvp"
    budget: float = 10.0
    rounds: int = 15
    project_type: str = "generic"
    tags: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    verify: dict[str, str] = Field(default_factory=dict)
    scoring: dict[str, Any] = Field(default_factory=dict)
    path: Optional[Path] = None


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "benchmarks" / "suite").is_dir():
            return parent
    return Path.cwd()


def suite_dir() -> Path:
    return repo_root() / "benchmarks" / "suite"


def runs_dir() -> Path:
    return repo_root() / "benchmarks" / "runs"


def discover_specs(suite: str = "standard", spec_id: str | None = None) -> list[BenchmarkSpec]:
    if suite != "standard":
        raise ValueError(f"Unknown suite {suite!r}")
    by_id: dict[str, BenchmarkSpec] = {}
    for path in sorted(suite_dir().glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        spec = BenchmarkSpec.model_validate({**data, "path": path})
        by_id[spec.id] = spec
    specs: list[BenchmarkSpec] = []
    for bid in STANDARD_SUITE_IDS:
        if bid not in by_id:
            raise FileNotFoundError(f"Missing benchmark spec: {bid}.yaml")
        specs.append(by_id[bid])
    if spec_id is not None:
        if spec_id not in by_id:
            raise ValueError(f"Unknown benchmark spec ID: {spec_id!r}")
        return [by_id[spec_id]]
    return specs


def has_llm_credentials() -> bool:
    from msc.runtime.llm_config import llm_credentials_ready  # noqa: PLC0415
    ready, _ = llm_credentials_ready()
    return ready


@dataclass
class BenchmarkRunOutcome:
    spec_id: str
    dry_run: bool
    workspace: Optional[Path]
    message: str
    skipped: bool = False


def _write_run_manifest(spec: BenchmarkSpec, outcome: BenchmarkRunOutcome) -> None:
    run_root = runs_dir() / spec.id
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "manifest.json").write_text(
        json.dumps(
            {
                "id": spec.id,
                "dry_run": outcome.dry_run,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "message": outcome.message,
                "skipped": outcome.skipped,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_benchmark(spec: BenchmarkSpec, *, dry_run: bool) -> BenchmarkRunOutcome:
    if dry_run:
        outcome = BenchmarkRunOutcome(spec.id, True, None, "dry-run: spec validated; no LLM invocation")
        _write_run_manifest(spec, outcome)
        return outcome
    if not has_llm_credentials():
        outcome = BenchmarkRunOutcome(spec.id, False, None, "skipped: no LLM API keys", True)
        _write_run_manifest(spec, outcome)
        return outcome
    workspace = runs_dir() / spec.id / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        from msc.runtime.company import MySoftwareCompany  # noqa: F401
    except ImportError:
        outcome = BenchmarkRunOutcome(
            spec.id,
            False,
            workspace,
            f"skipped: runtime not available — merge Phase 1 (org={spec.org}, budget={spec.budget})",
            True,
        )
        _write_run_manifest(spec, outcome)
        return outcome
    timeout_s = spec.rounds * 25  # generous: ~25s per round
    try:
        proc = subprocess.run(
            [
                "msc", "run", spec.idea.strip(),
                "--org", spec.org,
                f"--budget={spec.budget}",
                f"--rounds={spec.rounds}",
                "--no-human-review",
            ],
            cwd=repo_root(),
            env={**os.environ, "MSC_BENCHMARK_ID": spec.id, "MSC_BENCHMARK_WORKSPACE": str(workspace)},
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        msg = "completed via msc run" if proc.returncode == 0 else (proc.stderr or proc.stdout or "failed")
    except subprocess.TimeoutExpired as exc:
        # Partial output may still be usable — note timeout but don't fail hard.
        msg = f"timeout after {timeout_s}s — partial run (workspace may contain usable files)"
        exc.kill()
        proc = type("_FakeProc", (), {"returncode": 1, "stderr": msg, "stdout": ""})()  # type: ignore[assignment]
    outcome = BenchmarkRunOutcome(spec.id, False, workspace, msg, proc.returncode != 0)
    _write_run_manifest(spec, outcome)
    return outcome


def run_suite(
    *,
    suite: str = "standard",
    dry_run: bool = False,
    spec_id: str | None = None,
) -> list[BenchmarkRunOutcome]:
    return [run_benchmark(s, dry_run=dry_run) for s in discover_specs(suite=suite, spec_id=spec_id)]


def write_score(spec_id: str, *, compiles: bool, tests_pass: bool, requirements_met: int, polish_hours: float, llm_cost_usd: float, notes: str = "") -> Path:
    """Write a human score to benchmarks/runs/<id>/result.json."""
    run_root = runs_dir() / spec_id
    run_root.mkdir(parents=True, exist_ok=True)
    path = run_root / "result.json"
    existing: dict = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    existing.update(
        {
            "id": spec_id,
            "compiles": int(compiles),
            "tests_pass": int(tests_pass),
            "requirements_met": requirements_met,
            "polish_hours": polish_hours,
            "llm_cost_usd": llm_cost_usd,
            "notes": notes,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return path
