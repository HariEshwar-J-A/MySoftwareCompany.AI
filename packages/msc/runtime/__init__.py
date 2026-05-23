# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""MSC runtime: agency roles, company team, orchestrator, dry-run validation."""

from msc.runtime.dry_run import DryRunReport, run_dry_run

__all__ = [
    "DryRunReport",
    "run_dry_run",
]

try:
    from msc.runtime.agency_role import AgencyRoleZero
    from msc.runtime.company import (
        MySoftwareCompany,
        OrgHumanReviewConfig,
        OrgOrchestratorRef,
        OrgRoleRef,
        OrgTemplate,
        workspace_dir_for_org,
    )
    from msc.runtime.orchestrator import AgentsOrchestrator, NEXUS_ORCHESTRATOR_DOCTRINE

    __all__ += [
        "AgencyRoleZero",
        "AgentsOrchestrator",
        "MySoftwareCompany",
        "NEXUS_ORCHESTRATOR_DOCTRINE",
        "OrgHumanReviewConfig",
        "OrgOrchestratorRef",
        "OrgRoleRef",
        "OrgTemplate",
        "workspace_dir_for_org",
    ]
except Exception:
    pass
