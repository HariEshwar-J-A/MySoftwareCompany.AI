# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations  # noqa: I001

import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from msc.benchmarks.suite import BenchmarkSpec, discover_specs, repo_root, runs_dir

PASS_REQUIREMENTS_AVG = 2 / 3
PASS_POLISH_MEDIAN_HOURS = 8.0
NEEDS_HUMAN = "NEEDS_HUMAN_SCORE"


@dataclass
class BenchmarkScoreRow:
    spec_id: str
    name: str
    compiles: int | str
    tests_pass: int | str
    requirements_met: int | str
    polish_hours: float | str
    llm_cost_usd: float | str
    notes: str

    def requirements_numeric(self) -> float | None:
        return float(self.requirements_met) if isinstance(self.requirements_met, (int, float)) else None

    def polish_numeric(self) -> float | None:
        return float(self.polish_hours) if isinstance(self.polish_hours, (int, float)) else None


def collect_rows(suite: str = "standard") -> list[BenchmarkScoreRow]:
    rows: list[BenchmarkScoreRow] = []
    for spec in discover_specs(suite=suite):
        path = runs_dir() / spec.id / "result.json"
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "id": spec.id,
                        "requirements_met": NEEDS_HUMAN,
                        "polish_hours": NEEDS_HUMAN,
                        "notes": "Fill after human review.",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        result = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            BenchmarkScoreRow(
                spec.id,
                spec.name,
                result.get("compiles", NEEDS_HUMAN),
                result.get("tests_pass", NEEDS_HUMAN),
                result.get("requirements_met", NEEDS_HUMAN),
                result.get("polish_hours", NEEDS_HUMAN),
                result.get("llm_cost_usd", NEEDS_HUMAN),
                str(result.get("notes", "")),
            )
        )
    return rows


def aggregate_scores(rows: list[BenchmarkScoreRow]) -> dict[str, Any]:
    req = [r.requirements_numeric() for r in rows if r.requirements_numeric() is not None]
    pol = [r.polish_numeric() for r in rows if r.polish_numeric() is not None]
    return {
        "count": len(rows),
        "requirements_scored": len(req),
        "requirements_avg": statistics.mean(req) if req else None,
        "polish_scored": len(pol),
        "polish_median_hours": statistics.median(pol) if pol else None,
    }


def check_gate(rows: list[BenchmarkScoreRow]) -> dict[str, Any]:
    s = aggregate_scores(rows)
    missing = s["requirements_scored"] < s["count"] or s["polish_scored"] < s["count"]
    req_ok = s["requirements_avg"] is not None and s["requirements_avg"] >= PASS_REQUIREMENTS_AVG
    pol_ok = s["polish_median_hours"] is not None and s["polish_median_hours"] <= PASS_POLISH_MEDIAN_HOURS
    if missing:
        return {**s, "status": "INCOMPLETE", "passed": False, "reason": "Human scores required (NEEDS_HUMAN_SCORE)."}
    if req_ok and pol_ok:
        return {**s, "status": "PASS", "passed": True, "reason": "Meets Phase 2 gate threshold."}
    return {**s, "status": "FAIL", "passed": False, "reason": "Below pass threshold."}


def render_scorecard(*, suite: str = "standard") -> str:
    rows = collect_rows(suite=suite)
    gate = check_gate(rows)
    out = [
        "# MySoftwareCompany.AI Benchmark Scorecard",
        "",
        "Phase 2 **hard gate** before client sales.",
        "",
        "## Pass threshold (locked)",
        f"- Avg requirements met (0–3) ≥ **{PASS_REQUIREMENTS_AVG:.2f}**",
        f"- Median polish hours ≤ **{PASS_POLISH_MEDIAN_HOURS:.0f}h**",
        "",
        f"**Status:** {gate['status']}",
        "",
        gate["reason"],
        "",
        "| Build | Compiles | Tests | Req | Polish (h) | LLM $ | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        out.append(
            f"| {r.name} | {r.compiles} | {r.tests_pass} | {r.requirements_met} | "
            f"{r.polish_hours} | {r.llm_cost_usd} | {r.notes.replace('|', '/')} |"
        )
    out.extend(
        [
            "",
            "## Dry-run (CI, no API keys)",
            "```bash",
            "msc benchmark run --dry-run",
            "msc benchmark report",
            "msc benchmark gate",
            "```",
            "",
            "## Full runs",
            "Set API keys, merge Phase 1 runtime + vendor/MetaGPT, then `msc benchmark run`.",
            "Score each `benchmarks/runs/<id>/result.json` after human review.",
            "",
            f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        ]
    )
    return "\n".join(out) + "\n"


def write_scorecard(path: Path | None = None, *, suite: str = "standard") -> Path:
    target = path or repo_root() / "benchmarks" / "SCORECARD.md"
    target.write_text(render_scorecard(suite=suite), encoding="utf-8")
    return target
