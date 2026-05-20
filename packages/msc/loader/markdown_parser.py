# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Parse agency-agents markdown: YAML frontmatter + named sections."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from msc.loader.agent_spec import AgentSpec

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)

_RAW_INSTRUCTION_CHAR_LIMIT = 6000

_SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "identity": ("identity", "memory"),
    "core_mission": ("core mission", "core beliefs"),
    "critical_rules": ("critical rules", "mandatory process"),
    "deliverables": (
        "core capabilities",
        "capabilities",
        "deliverables",
        "technical deliverables",
    ),
    "workflow": ("workflow process", "workflow phases", "your workflow", "workflow"),
    "communication_style": ("communication style",),
    "success_metrics": ("success metrics",),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _normalize_heading(title: str) -> str:
    text = re.sub(r"[^\w\s]", " ", title.lower())
    return " ".join(text.split())


def _match_section_key(heading: str) -> str | None:
    normalized = _normalize_heading(heading)
    for key, aliases in _SECTION_ALIASES.items():
        if any(alias in normalized for alias in aliases):
            return key
    return None


def _split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(_SECTION_RE.finditer(body))
    if not matches:
        return sections

    for index, match in enumerate(matches):
        key = _match_section_key(match.group(1))
        if not key:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        if content:
            sections[key] = content
    return sections


def _extract_critical_rules(section_text: str) -> list[str]:
    rules: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            item = stripped.lstrip("-*").strip()
            if item:
                rules.append(item)
        elif stripped.startswith("###"):
            continue
        elif rules and stripped and not stripped.startswith("#"):
            rules[-1] = f"{rules[-1]} {stripped}"
    if rules:
        return rules

    for match in _BULLET_RE.finditer(section_text):
        text = match.group(1).strip()
        if text:
            rules.append(text)
    return rules


def _slug_from_path(path: Path, agents_root: Path) -> str:
    return path.relative_to(agents_root).stem


def _division_from_path(path: Path, agents_root: Path) -> str:
    rel = path.relative_to(agents_root)
    if len(rel.parts) > 1:
        return rel.parts[0]
    return "general"


def _assemble_raw_instruction(
    name: str,
    description: str,
    vibe: str,
    sections: dict[str, str],
    critical_rules: list[str],
) -> str:
    parts: list[str] = [f"You are **{name}**."]
    if description:
        parts.append(description)
    if vibe:
        parts.append(f"Tone: {vibe}")

    section_labels = {
        "identity": "Identity",
        "core_mission": "Core Mission",
        "deliverables": "Deliverables",
        "workflow": "Workflow",
        "communication_style": "Communication Style",
        "success_metrics": "Success Metrics",
    }
    for key, label in section_labels.items():
        body = sections.get(key, "")
        if body:
            parts.append(f"## {label}\n{body}")

    if critical_rules:
        bullets = "\n".join(f"- {rule}" for rule in critical_rules)
        parts.append(f"## Critical Rules\n{bullets}")

    return "\n\n".join(parts).strip()


def _trim_raw_instruction(text: str, limit: int = _RAW_INSTRUCTION_CHAR_LIMIT) -> str:
    if len(text) <= limit:
        return text
    trimmed = text[: limit - 3].rstrip()
    return f"{trimmed}..."


def parse_agent_markdown(
    text: str,
    *,
    path: Path | str,
    agents_root: Path | None = None,
) -> AgentSpec:
    """Parse a single agency-agents markdown file into an AgentSpec."""
    file_path = Path(path)
    root = agents_root or file_path.parent

    frontmatter: dict[str, object] = {}
    body = text
    match = _FRONTMATTER_RE.match(text)
    if match:
        loaded = yaml.safe_load(match.group(1)) or {}
        if isinstance(loaded, dict):
            frontmatter = loaded
        body = text[match.end() :]

    sections = _split_sections(body)
    critical_rules = _extract_critical_rules(sections.get("critical_rules", ""))

    name = str(frontmatter.get("name") or file_path.stem.replace("-", " ").title())
    description = str(frontmatter.get("description") or "")
    vibe = str(frontmatter.get("vibe") or "")
    color = str(frontmatter.get("color") or "")
    emoji = str(frontmatter.get("emoji") or "")

    try:
        slug = _slug_from_path(file_path, root)
        division = _division_from_path(file_path, root)
    except ValueError:
        slug = file_path.stem
        division = "general"

    repo_root = _repo_root()
    try:
        rel_path = str(file_path.relative_to(repo_root))
    except ValueError:
        rel_path = str(file_path)

    raw_instruction = _trim_raw_instruction(
        _assemble_raw_instruction(name, description, vibe, sections, critical_rules)
    )

    return AgentSpec(
        name=name,
        slug=slug,
        division=division,
        description=description,
        vibe=vibe,
        path=rel_path,
        identity=sections.get("identity", ""),
        core_mission=sections.get("core_mission", ""),
        critical_rules=critical_rules,
        deliverables=sections.get("deliverables", ""),
        workflow=sections.get("workflow", ""),
        communication_style=sections.get("communication_style", ""),
        success_metrics=sections.get("success_metrics", ""),
        raw_instruction=raw_instruction,
        color=color,
        emoji=emoji,
    )


def parse_agent_file(path: Path, *, agents_root: Path | None = None) -> AgentSpec:
    """Load and parse an agent markdown file from disk."""
    file_path = Path(path)
    root = agents_root or _infer_agents_root(file_path)
    text = file_path.read_text(encoding="utf-8")
    return parse_agent_markdown(text, path=file_path, agents_root=root)


def _infer_agents_root(path: Path) -> Path:
    for parent in path.parents:
        if parent.name == "agency-agents":
            return parent
    return path.parent
