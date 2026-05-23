# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Lightweight deliverable checks before marking a run completed."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

_IGNORED_PARTS = frozenset({".msc", "__pycache__", ".git", "node_modules"})
# Metadata files we write ourselves — never count as deliverable evidence.
_OWN_METADATA = frozenset({"metadata.json"})
_SOURCE_SUFFIXES = frozenset({".html", ".htm", ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md"})
# At least one of these suffixes must be present for a run to be considered a real deliverable.
_CODE_SUFFIXES = frozenset({".html", ".htm", ".py", ".js", ".jsx", ".ts", ".tsx"})
_SCRIPT_TAG_RE = re.compile(r"<script([^>]*)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
_JSX_IN_JS_RE = re.compile(r"<\s*[A-Za-z][\w.-]*")
_BABEL_RE = re.compile(r"babel(?:\.min)?\.js|@babel/standalone", re.IGNORECASE)


class DeliverableCheckError(Exception):
    """Raised when workspace artifacts fail deliverable verification."""

    def __init__(self, report: "DeliverableReport"):
        self.report = report
        issues = report.errors + report.warnings
        super().__init__("; ".join(issues) if issues else "deliverable check failed")


@dataclass
class DeliverableReport:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    files_checked: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "files_checked": list(self.files_checked),
        }


class _LenientHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []

    def error(self, message: str) -> None:  # pragma: no cover - py version dependent
        self.errors.append(message)


def _iter_source_files(workspace: Path) -> list[Path]:
    files: list[Path] = []
    if not workspace.is_dir():
        return files
    for path in workspace.rglob("*"):
        if not path.is_file():
            continue
        if _IGNORED_PARTS.intersection(path.relative_to(workspace).parts):
            continue
        if path.name.startswith(".") and path.name not in {".gitkeep"}:
            continue
        if path.name in _OWN_METADATA:
            continue
        if path.suffix.lower() in _SOURCE_SUFFIXES or path.name in {"Makefile", "Dockerfile"}:
            files.append(path)
    return sorted(files)


def _check_html(path: Path, report: DeliverableReport) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = str(path.name)

    parser = _LenientHTMLParser()
    try:
        parser.feed(text)
    except Exception as exc:  # noqa: BLE001
        report.errors.append(f"{rel}: HTML parse error: {exc}")

    has_babel = bool(_BABEL_RE.search(text))
    for match in _SCRIPT_TAG_RE.finditer(text):
        attrs, body = match.group(1), match.group(2)
        if re.search(r"""type\s*=\s*['"]text/babel['"]""", attrs, re.IGNORECASE):
            continue
        if not body.strip():
            continue
        if _JSX_IN_JS_RE.search(body):
            if has_babel:
                report.warnings.append(
                    f"{rel}: JSX in script tag but Babel is present — verify type=text/babel"
                )
            else:
                report.errors.append(
                    f"{rel}: JSX in plain <script> without Babel — file will not run in a browser"
                )


def _check_python(path: Path, report: DeliverableReport) -> None:
    rel = str(path.name)
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        compile(source, rel, "exec")
    except SyntaxError as exc:
        report.errors.append(f"{rel}: Python syntax error: {exc.msg} (line {exc.lineno})")


def verify_workspace_deliverables(workspace: Path | str) -> DeliverableReport:
    """Return a report; ok is False when errors are present."""
    root = Path(workspace).expanduser().resolve()
    report = DeliverableReport(ok=True)

    sources = _iter_source_files(root)
    if not sources:
        report.errors.append("no deliverable source files found in workspace")
        report.ok = False
        return report

    has_code = any(p.suffix.lower() in _CODE_SUFFIXES for p in sources)
    if not has_code:
        report.errors.append(
            "workspace contains only docs/data files (json, md) — no executable code found"
        )
        report.ok = False
        return report

    for path in sources:
        rel = path.relative_to(root).as_posix()
        report.files_checked.append(rel)
        suffix = path.suffix.lower()
        if suffix in {".html", ".htm"}:
            _check_html(path, report)
        elif suffix == ".py":
            _check_python(path, report)

    if report.errors:
        report.ok = False
    return report
