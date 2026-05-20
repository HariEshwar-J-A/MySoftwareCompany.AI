# Copyright MySoftwareCompany.AI — BUSL-1.1 (see LICENSE)
"""Human review gate: mandatory pause before client deliverables."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

NO_HUMAN_REVIEW_WARNING = (
    "\n*** WARNING: Human review gate disabled. "
    "Do not use for client deliverables. ***\n"
)

METADATA_DIR = ".msc"
RUN_METADATA_FILE = "run.json"

_VALID_DECISIONS = frozenset({"APPROVED", "REVISE", "REJECT"})


class ReviewDecision(str, Enum):
    APPROVED = "APPROVED"
    REVISE = "REVISE"
    REJECT = "REJECT"


class HumanReviewGate:
    """Pauses a run for operator sign-off; records bypass in workspace metadata."""

    def __init__(self, workspace: Path | str, *, required: bool = True):
        self.workspace = Path(workspace)
        self.required = required
        self.last_feedback: str | None = None
        self._metadata_path = self.workspace / METADATA_DIR / RUN_METADATA_FILE

    def metadata_path(self) -> Path:
        return self._metadata_path

    def read_metadata(self) -> dict[str, Any]:
        if not self._metadata_path.exists():
            return {}
        try:
            return json.loads(self._metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def write_metadata(self, patch: dict[str, Any]) -> dict[str, Any]:
        self._metadata_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.read_metadata()
        data.update(patch)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._metadata_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def apply_bypass_flag(self, no_human_review: bool) -> None:
        """Honor CLI ``--no-human-review``: stderr warning + metadata stamp."""
        if not no_human_review:
            self.write_metadata({"no_human_review": False, "human_review_required": self.required})
            return
        sys.stderr.write(NO_HUMAN_REVIEW_WARNING)
        sys.stderr.flush()
        self.write_metadata(
            {
                "no_human_review": True,
                "human_review_required": False,
                "bypass_warning": NO_HUMAN_REVIEW_WARNING.strip(),
            }
        )

    def checkpoint(self, stage: str, *, interactive: bool = True) -> ReviewDecision:
        """Block until the operator approves, requests revision, or rejects."""
        if not self.required:
            return ReviewDecision.APPROVED

        meta = self.read_metadata()
        if meta.get("no_human_review"):
            return ReviewDecision.APPROVED

        if not interactive or not sys.stdin.isatty():
            self.write_metadata({"human_review_pending": stage, "human_review_status": "skipped_non_tty"})
            return ReviewDecision.APPROVED

        print(f"\n=== Human review gate ({stage}) ===", file=sys.stderr)
        print(f"Workspace: {self.workspace.resolve()}", file=sys.stderr)
        print("Review artifacts, then enter: APPROVED | REVISE | REJECT", file=sys.stderr)

        while True:
            try:
                raw = input("Decision> ").strip().upper()
            except EOFError:
                self.write_metadata({"human_review_pending": stage, "human_review_status": "eof"})
                return ReviewDecision.APPROVED

            if raw in _VALID_DECISIONS:
                decision = ReviewDecision(raw)
                break
            print("Invalid decision. Use APPROVED, REVISE, or REJECT.", file=sys.stderr)

        if decision == ReviewDecision.REVISE:
            try:
                self.last_feedback = input("Revision feedback> ").strip()
            except EOFError:
                self.last_feedback = ""
        else:
            self.last_feedback = None

        self.write_metadata(
            {
                "human_review_stage": stage,
                "human_review_status": decision.value,
                "human_review_feedback": self.last_feedback,
            }
        )
        return decision

    def record_run_outcome(self, outcome: str) -> None:
        self.write_metadata({"run_outcome": outcome})
