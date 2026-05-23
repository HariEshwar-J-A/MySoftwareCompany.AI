"""Tests for deliverable verification and workspace path resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from msc.review.deliverable import DeliverableCheckError, verify_workspace_deliverables
from msc.review.gate import HumanReviewGate
from msc.runtime.org_model import resolve_workspace_root, workspace_dir_for_org


BROKEN_JSX_HTML = """<!DOCTYPE html>
<html><body>
<script>
function App() {
  return (<div>Hello</div>);
}
</script>
</body></html>
"""

VALID_CREATE_ELEMENT_HTML = """<!DOCTYPE html>
<html><body>
<script>
ReactDOM.render(React.createElement('div', null, 'ok'), document.body);
</script>
</body></html>
"""


def test_workspace_dir_is_absolute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    nested = tmp_path / "nested" / "deep"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    ws = workspace_dir_for_org("startup-mvp", tmp_path / "workspace")
    assert ws.is_absolute()
    assert ws == (tmp_path / "workspace" / "startup-mvp").resolve()


def test_resolve_workspace_root_expands_user() -> None:
    resolved = resolve_workspace_root("~/tmp-ws")
    assert resolved.is_absolute()
    assert str(resolved).endswith("tmp-ws")


def test_deliverable_check_flags_jsx_without_babel(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(BROKEN_JSX_HTML)
    report = verify_workspace_deliverables(tmp_path)
    assert report.ok is False
    assert any("JSX" in err for err in report.errors)


def test_deliverable_check_passes_create_element_html(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(VALID_CREATE_ELEMENT_HTML)
    report = verify_workspace_deliverables(tmp_path)
    assert report.ok is True
    assert report.errors == []


def test_deliverable_check_no_source_files(tmp_path: Path) -> None:
    report = verify_workspace_deliverables(tmp_path)
    assert report.ok is False
    assert any("no deliverable" in w for w in report.warnings)


def test_deliverable_check_error_message(tmp_path: Path) -> None:
    (tmp_path / "index.html").write_text(BROKEN_JSX_HTML)
    report = verify_workspace_deliverables(tmp_path)
    err = DeliverableCheckError(report)
    assert "JSX" in str(err)


def test_bypass_does_not_record_approved(tmp_path: Path) -> None:
    gate = HumanReviewGate(tmp_path)
    gate.apply_bypass_flag(True)
    meta = gate.read_metadata()
    assert meta["human_review_status"] == "bypassed"
    assert meta["no_human_review"] is True
    gate.record_run_outcome("completed", no_human_review=True)
    meta = json.loads((tmp_path / ".msc" / "run.json").read_text())
    assert meta["run_outcome"] == "completed_unreviewed"
    assert meta.get("human_review_status") != "APPROVED"
