# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Execute a full org run via MySoftwareCompany + MetaGPT."""

from __future__ import annotations

from msc.config import MSCConfig
from msc.loader.org_template import OrgTemplate as LoaderOrgTemplate
from msc.loader.runtime_bridge import make_load_spec, to_runtime_template
from msc.runtime.company import MySoftwareCompany


async def run_org_project(
    idea: str,
    template: LoaderOrgTemplate,
    config: MSCConfig,
    *,
    budget: float | None = None,
    rounds: int | None = None,
    no_human_review: bool = False,
) -> MySoftwareCompany:
    """Bootstrap roster, run MetaGPT rounds, and apply human-review gate."""
    runtime_template = to_runtime_template(template)
    if budget is not None:
        runtime_template.budget_default = budget

    company = MySoftwareCompany.from_org(runtime_template, workspace_root=config.workspace_root)
    load_spec = make_load_spec(config)
    await company.run_with_review(
        idea,
        n_round=rounds or config.default_rounds,
        load_spec=load_spec,
        no_human_review=no_human_review,
    )
    return company
