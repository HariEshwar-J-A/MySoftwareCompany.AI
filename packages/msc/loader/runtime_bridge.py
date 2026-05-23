# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Bridge loader OrgTemplate / agent paths to runtime MySoftwareCompany types."""

from __future__ import annotations

from pathlib import Path

from msc.config import MSCConfig
from msc.loader.agent_spec import AgentSpec
from msc.loader.catalog import catalog_root, get_agent
from msc.loader.markdown_parser import parse_agent_file
from msc.loader.org_template import OrgTemplate as LoaderOrgTemplate
from msc.runtime.org_model import (
    LoadSpecFn,
    OrgHumanReviewConfig,
    OrgOrchestratorRef,
    OrgRoleRef,
    OrgTemplate as RuntimeOrgTemplate,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]


def to_runtime_template(spec: LoaderOrgTemplate) -> RuntimeOrgTemplate:
    """Convert YAML-loaded org spec into runtime dataclass used by MySoftwareCompany."""
    return RuntimeOrgTemplate(
        name=spec.name,
        description=spec.description,
        budget_default=spec.budget_default,
        orchestrator=OrgOrchestratorRef(
            agent=spec.orchestrator.agent,
            metagpt_class=spec.orchestrator.metagpt_class,
        ),
        roles=[
            OrgRoleRef(
                agent=r.agent,
                tools=list(r.tools),
                llm_tier=r.llm_tier,
                role=r.role,
            )
            for r in spec.roles
        ],
        human_review=OrgHumanReviewConfig(
            required=spec.human_review.required,
            before=list(spec.human_review.before),
        ),
    )


def make_load_spec(config: MSCConfig) -> LoadSpecFn:
    """Resolve org YAML agent paths (or slugs) to parsed AgentSpec objects."""

    agents_root = catalog_root(config.agency_agents_root)

    def load_spec(agent_ref: str) -> AgentSpec:
        path = Path(agent_ref)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        if path.is_file():
            return parse_agent_file(path, agents_root=agents_root)
        spec = get_agent(Path(agent_ref).stem, agents_root=config.agency_agents_root)
        if spec is None:
            raise FileNotFoundError(f"Agent not found: {agent_ref}")
        return spec

    return load_spec
