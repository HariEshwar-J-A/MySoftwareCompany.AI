# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Optional console verbosity for MetaGPT / loguru (MSC_LOG_LEVEL, --log-level, -v/-q)."""

from __future__ import annotations

import os
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]

VALID_LOG_LEVELS: tuple[LogLevel, ...] = ("DEBUG", "INFO", "WARNING", "ERROR")
# Console: WARNING by default (no INFO spam). File logs stay INFO via _file_log_level().
_DEFAULT_CONSOLE_LEVEL: LogLevel = "WARNING"
_DEFAULT_FILE_LEVEL: LogLevel = "INFO"
_ENV_VAR = "MSC_LOG_LEVEL"


def normalize_log_level(value: str | None) -> LogLevel | None:
    if not value or not str(value).strip():
        return None
    level = str(value).strip().upper()
    if level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid log level {value!r}. Choose one of: {', '.join(VALID_LOG_LEVELS)}"
        )
    return level  # type: ignore[return-value]


def resolve_log_level(
    *,
    log_level: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
    info: bool = False,
) -> LogLevel:
    """Resolve console level from CLI flags, then MSC_LOG_LEVEL env, then WARNING default."""
    flags = sum((verbose, quiet, info))
    if flags > 1:
        raise ValueError("Use only one of --verbose, --quiet, and --info.")
    if verbose:
        return "DEBUG"
    if quiet:
        return "ERROR"
    if info:
        return "INFO"
    from_env = normalize_log_level(os.environ.get(_ENV_VAR))
    if from_cli := normalize_log_level(log_level):
        return from_cli
    return from_env or _DEFAULT_CONSOLE_LEVEL


def resolve_file_log_level(console_level: LogLevel, *, log_level: str | None = None) -> LogLevel:
    """File log level: INFO by default; follows console when explicitly set via --log-level."""
    if from_cli := normalize_log_level(log_level):
        return from_cli
    if console_level == "DEBUG":
        return "DEBUG"
    if console_level == "ERROR":
        return "ERROR"
    return _DEFAULT_FILE_LEVEL


def apply_log_level(console_level: LogLevel, *, file_level: LogLevel | None = None) -> LogLevel:
    """Configure MetaGPT/loguru. Sets MSC_LOG_LEVEL to the console level for child processes."""
    file_lvl = file_level or _DEFAULT_FILE_LEVEL
    os.environ[_ENV_VAR] = console_level
    try:
        from metagpt.logs import define_log_level

        define_log_level(print_level=console_level, logfile_level=file_lvl)
    except ImportError:
        pass
    return console_level


def configure_logging(
    *,
    log_level: str | None = None,
    verbose: bool = False,
    quiet: bool = False,
    info: bool = False,
) -> LogLevel:
    """Resolve and apply logging configuration."""
    console = resolve_log_level(
        log_level=log_level, verbose=verbose, quiet=quiet, info=info
    )
    file_lvl = resolve_file_log_level(console, log_level=log_level)
    return apply_log_level(console, file_level=file_lvl)
