# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Agency-agents markdown loader: parse personas and index the catalog."""

from msc.loader.agent_spec import AgentSpec
from msc.loader.catalog import (
    catalog_root,
    get_agent,
    is_excluded_path,
    iter_agent_paths,
    list_agents,
    list_divisions,
    load_agent_markdown,
)
from msc.loader.markdown_parser import parse_agent_file, parse_agent_markdown

__all__ = [
    "AgentSpec",
    "catalog_root",
    "get_agent",
    "is_excluded_path",
    "iter_agent_paths",
    "list_agents",
    "list_divisions",
    "load_agent_markdown",
    "parse_agent_file",
    "parse_agent_markdown",
]
