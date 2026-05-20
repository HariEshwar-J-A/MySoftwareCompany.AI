# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""CLI entry point — benchmark commands via hook; other commands land in Phase 1."""

from __future__ import annotations

import typer

from msc import __version__

app = typer.Typer(
    name="mscai",
    help="MySoftwareCompany.AI — run AI software agencies from the terminal.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """MySoftwareCompany.AI CLI."""


@app.command()
def version() -> None:
    """Print package version."""
    typer.echo(f"mscai {__version__}")


from msc.benchmarks.cli import register_benchmark_commands  # noqa: E402

register_benchmark_commands(app)

if __name__ == "__main__":
    app()
