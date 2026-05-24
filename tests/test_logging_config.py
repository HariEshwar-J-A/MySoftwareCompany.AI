# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from msc.logging_config import (
    configure_logging,
    resolve_file_log_level,
    resolve_log_level,
)


def test_resolve_default_console_warning() -> None:
    assert resolve_log_level() == "WARNING"


def test_verbose_and_quiet_conflict() -> None:
    with pytest.raises(ValueError, match="only one"):
        resolve_log_level(verbose=True, quiet=True)


def test_verbose_is_debug() -> None:
    assert resolve_log_level(verbose=True) == "DEBUG"


def test_quiet_is_error() -> None:
    assert resolve_log_level(quiet=True) == "ERROR"


def test_info_flag() -> None:
    assert resolve_log_level(info=True) == "INFO"


def test_cli_overrides_env(monkeypatch) -> None:
    monkeypatch.setenv("MSC_LOG_LEVEL", "ERROR")
    assert resolve_log_level(log_level="debug") == "DEBUG"


def test_env_when_no_cli(monkeypatch) -> None:
    monkeypatch.setenv("MSC_LOG_LEVEL", "INFO")
    assert resolve_log_level() == "INFO"


def test_file_level_info_when_console_warning() -> None:
    assert resolve_file_log_level("WARNING") == "INFO"


def test_file_level_follows_explicit_log_level() -> None:
    assert resolve_file_log_level("WARNING", log_level="debug") == "DEBUG"


def test_configure_sets_console_env(monkeypatch) -> None:
    monkeypatch.delenv("MSC_LOG_LEVEL", raising=False)
    with patch("msc.logging_config.apply_log_level") as mock_apply:
        mock_apply.return_value = "WARNING"
        level = configure_logging()
        assert level == "WARNING"
        mock_apply.assert_called_once()
        assert mock_apply.call_args.kwargs["file_level"] == "INFO"


def test_configure_default_sets_warning(monkeypatch) -> None:
    monkeypatch.delenv("MSC_LOG_LEVEL", raising=False)
    level = configure_logging()
    assert level == "WARNING"
    assert os.environ["MSC_LOG_LEVEL"] == "WARNING"
