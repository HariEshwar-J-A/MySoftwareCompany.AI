# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""MSC runtime: agency roles, company team, orchestrator, dry-run validation."""

from msc.runtime.dry_run import DryRunReport, run_dry_run
from msc.runtime.org_model import (
    OrgHumanReviewConfig,
    OrgOrchestratorRef,
    OrgRoleRef,
    OrgTemplate,
    workspace_dir_for_org,
)

__all__ = [
    "DryRunReport",
    "OrgHumanReviewConfig",
    "OrgOrchestratorRef",
    "OrgRoleRef",
    "OrgTemplate",
    "run_dry_run",
    "workspace_dir_for_org",
]

try:
    from msc.runtime.agency_role import AgencyRoleZero
    from msc.runtime.company import MySoftwareCompany
    from msc.runtime.orchestrator import AgentsOrchestrator, NEXUS_ORCHESTRATOR_DOCTRINE

    __all__ += [
        "AgencyRoleZero",
        "AgentsOrchestrator",
        "MySoftwareCompany",
        "NEXUS_ORCHESTRATOR_DOCTRINE",
    ]
except Exception:
    pass
