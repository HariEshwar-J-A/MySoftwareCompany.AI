# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Quality gates: deliverable verification with configurable retries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from msc.review.deliverable import DeliverableCheckError, DeliverableReport, verify_workspace_deliverables
from msc.runtime.org_model import OrgGatesConfig

if TYPE_CHECKING:
    from msc.runtime.company import MySoftwareCompany


@dataclass
class GateResult:
    passed: bool
    attempts: int
    report: DeliverableReport
    retries_used: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "attempts": self.attempts,
            "retries_used": self.retries_used,
            "deliverable_check": self.report.to_dict(),
        }


async def run_deliverable_gate(
    company: MySoftwareCompany,
    gates: OrgGatesConfig | None,
    *,
    extra_rounds_per_retry: int = 3,
) -> GateResult:
    """Verify workspace deliverables; optionally retry with extra MetaGPT rounds."""
    max_retries = gates.max_retries if gates else 0
    require_evidence = gates.require_evidence if gates else True

    if not require_evidence:
        empty = DeliverableReport(ok=True, files_checked=[])
        return GateResult(passed=True, attempts=0, report=empty)

    report = verify_workspace_deliverables(company.workspace)
    if report.ok:
        return GateResult(passed=True, attempts=1, report=report)

    retries_used = 0
    while retries_used < max_retries and not report.ok:
        retries_used += 1
        feedback = (
            "[Quality gate — REVISE]\n"
            "Deliverable check failed. Fix these issues before marking complete:\n"
            + "\n".join(f"- {e}" for e in report.errors)
            + "\n".join(f"- (warn) {w}" for w in report.warnings)
        )
        company._publish_review_feedback(feedback)
        await company.run(n_round=extra_rounds_per_retry)
        report = verify_workspace_deliverables(company.workspace)

    return GateResult(
        passed=report.ok,
        attempts=1 + retries_used,
        report=report,
        retries_used=retries_used,
    )


def raise_if_gate_failed(result: GateResult) -> None:
    if not result.passed:
        raise DeliverableCheckError(result.report)
