# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from msc.benchmarks.scorer import check_gate, collect_rows, write_scorecard
from msc.benchmarks.suite import discover_specs, has_llm_credentials, run_suite

console = Console()
benchmark_app = typer.Typer(
    name="benchmark",
    help="Phase 2 quality benchmark suite (hard gate before client sales).",
    no_args_is_help=True,
)


@benchmark_app.command("list")
def benchmark_list(suite: str = typer.Option("standard", "--suite")) -> None:
    table = Table(title=f"Benchmark suite: {suite}")
    for col in ("ID", "Name", "Type", "Org", "Budget"):
        table.add_column(col)
    for spec in discover_specs(suite=suite):
        table.add_row(spec.id, spec.name, spec.project_type, spec.org, str(spec.budget))
    console.print(table)


@benchmark_app.command("run")
def benchmark_run(
    suite: str = typer.Option("standard", "--suite"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    if dry_run:
        console.print("[bold]Dry-run mode[/bold] — no LLM calls.")
    elif not has_llm_credentials():
        console.print("[yellow]No LLM API keys — runs will be skipped.[/yellow]")
    for outcome in run_suite(suite=suite, dry_run=dry_run):
        style = "green" if not outcome.skipped else "yellow"
        console.print(f"[{style}]{outcome.spec_id}[/{style}]: {outcome.message}")
    write_scorecard(suite=suite)
    console.print("Updated benchmarks/SCORECARD.md")


@benchmark_app.command("report")
def benchmark_report(suite: str = typer.Option("standard", "--suite")) -> None:
    console.print(f"Wrote {write_scorecard(suite=suite)}")


@benchmark_app.command("gate")
def benchmark_gate(suite: str = typer.Option("standard", "--suite")) -> None:
    gate = check_gate(collect_rows(suite=suite))
    console.print(f"Gate status: [bold]{gate['status']}[/bold] — {gate['reason']}")
    if not gate["passed"]:
        raise typer.Exit(1)


def register_benchmark_commands(root_app: typer.Typer) -> None:
    root_app.add_typer(benchmark_app, name="benchmark")
