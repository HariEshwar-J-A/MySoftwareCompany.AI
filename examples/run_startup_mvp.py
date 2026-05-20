#!/usr/bin/env python3
"""SDK example: validate startup-mvp org wiring (no LLM calls).

Full end-to-end run:
  msc run "Build a todo MVP" --org startup-mvp --budget 15

Dry-run only (works on feat/cli-orgs):
  python examples/run_startup_mvp.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages"))

from msc.config import MSCConfig
from msc.loader.org_template import load_org_template
from msc.runtime.dry_run import format_report, run_dry_run


def main() -> int:
    config = MSCConfig(orgs_root=REPO_ROOT / "orgs")
    template = load_org_template("startup-mvp", config)
    print(f"Loaded org: {template.name} — {template.description}")
    report = run_dry_run("startup-mvp", config)
    print(format_report(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
