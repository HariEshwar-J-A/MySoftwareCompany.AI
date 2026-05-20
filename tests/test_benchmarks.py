# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from pathlib import Path

from msc.benchmarks.scorer import PASS_POLISH_MEDIAN_HOURS, PASS_REQUIREMENTS_AVG, check_gate, collect_rows
from msc.benchmarks.suite import STANDARD_SUITE_IDS, discover_specs, run_suite


def test_six_specs():
    assert [s.id for s in discover_specs()] == list(STANDARD_SUITE_IDS)


def test_dry_run_manifests(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[1]
    (tmp_path / "benchmarks" / "suite").mkdir(parents=True)
    for name in STANDARD_SUITE_IDS:
        (tmp_path / "benchmarks" / "suite" / f"{name}.yaml").write_text(
            (repo / "benchmarks" / "suite" / f"{name}.yaml").read_text()
        )
    monkeypatch.setattr("msc.benchmarks.suite.repo_root", lambda: tmp_path)
    monkeypatch.setattr("msc.benchmarks.scorer.repo_root", lambda: tmp_path)
    assert len(run_suite(dry_run=True)) == 6


def test_gate_incomplete():
    g = check_gate(collect_rows())
    assert g["status"] == "INCOMPLETE" and not g["passed"]


def test_thresholds():
    assert PASS_REQUIREMENTS_AVG == 2 / 3 and PASS_POLISH_MEDIAN_HOURS == 8.0
