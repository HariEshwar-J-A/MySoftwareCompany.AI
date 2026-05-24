# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

from __future__ import annotations

import time
from typing import Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from msc.benchmarks.scorer import MIN_SCORED_FOR_PRELIMINARY, check_gate, collect_rows, write_scorecard
from msc.benchmarks.suite import (
    STANDARD_SUITE_IDS,
    benchmark_timeout_seconds,
    discover_specs,
    has_llm_credentials,
    run_benchmark,
    write_score,
)

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
    spec: Optional[str] = typer.Option(None, "--spec", help=f"Run a single spec ID. Choices: {', '.join(STANDARD_SUITE_IDS)}"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    if dry_run:
        console.print("[bold]Dry-run mode[/bold] — no LLM calls.")
    elif not has_llm_credentials():
        console.print("[yellow]No LLM API keys — runs will be skipped.[/yellow]")
    specs = discover_specs(suite=suite, spec_id=spec or None)
    total = len(specs)
    if spec:
        console.print(f"Running single spec: [bold]{spec}[/bold]")
    elif total:
        console.print(f"Running [bold]{total}[/bold] benchmark spec(s) from suite [bold]{suite}[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    ) as progress:
        suite_task = progress.add_task("Benchmark suite", total=total)
        for index, bench_spec in enumerate(specs, start=1):
            timeout_s = benchmark_timeout_seconds(bench_spec)
            progress.update(
                suite_task,
                description=f"Spec {index}/{total}: {bench_spec.id} (≤{timeout_s}s)",
            )
            console.print(
                f"\n[bold cyan]▶ {index}/{total}[/bold cyan] [bold]{bench_spec.id}[/bold] "
                f"[dim](rounds={bench_spec.rounds}, timeout={timeout_s}s, org={bench_spec.org})[/dim]"
            )
            started = time.monotonic()
            outcome = run_benchmark(bench_spec, dry_run=dry_run)
            elapsed_s = int(time.monotonic() - started)
            progress.advance(suite_task)
            style = "green" if not outcome.skipped else "yellow"
            console.print(
                f"[{style}]{outcome.spec_id}[/{style}]: {outcome.message} "
                f"[dim]({elapsed_s}s / {timeout_s}s)[/dim]"
            )
    write_scorecard(suite=suite)
    console.print("Updated benchmarks/SCORECARD.md")


@benchmark_app.command("score")
def benchmark_score(
    spec_id: str = typer.Argument(help=f"Spec to score. Choices: {', '.join(STANDARD_SUITE_IDS)}"),
    compiles: bool = typer.Option(..., "--compiles/--no-compiles", help="Did the output compile / open without error?"),
    tests: bool = typer.Option(..., "--tests/--no-tests", help="Do the automated/manual tests pass?"),
    req: int = typer.Option(..., "--req", help="Requirements met 0–3 (0=none, 1=some, 2=most, 3=all)."),
    polish: float = typer.Option(..., "--polish", help="Estimated hours to bring to client-ready polish."),
    cost: float = typer.Option(0.0, "--cost", help="Actual LLM cost in USD from your dashboard."),
    notes: str = typer.Option("", "--notes", help="Free-text notes about the output."),
    suite: str = typer.Option("standard", "--suite"),
) -> None:
    """Record your human score for a benchmark run.

    Example:

        msc benchmark score todo-cli --compiles --tests --req 2 --polish 3 --cost 0.04
    """
    if req not in (0, 1, 2, 3):
        console.print("[red]--req must be 0, 1, 2, or 3[/red]")
        raise typer.Exit(1)
    path = write_score(
        spec_id,
        compiles=compiles,
        tests_pass=tests,
        requirements_met=req,
        polish_hours=polish,
        llm_cost_usd=cost,
        notes=notes,
    )
    console.print(f"[green]Score saved:[/green] {path}")
    scorecard = write_scorecard(suite=suite)
    gate = check_gate(collect_rows(suite=suite))
    console.print(f"Updated {scorecard}")
    console.print(f"Gate status: [bold]{gate['status']}[/bold] — {gate['reason']}")


@benchmark_app.command("report")
def benchmark_report(suite: str = typer.Option("standard", "--suite")) -> None:
    console.print(f"Wrote {write_scorecard(suite=suite)}")


@benchmark_app.command("gate")
def benchmark_gate(
    suite: str = typer.Option("standard", "--suite"),
    preliminary: bool = typer.Option(False, "--preliminary", help=f"Show gate status with ≥{MIN_SCORED_FOR_PRELIMINARY} scored runs."),
) -> None:
    gate = check_gate(collect_rows(suite=suite), preliminary=preliminary)
    req_avg = gate.get("requirements_avg")
    pol_med = gate.get("polish_median_hours")
    if req_avg is not None:
        console.print(f"  Avg requirements met: {req_avg:.2f} (threshold ≥ 0.67)")
    if pol_med is not None:
        console.print(f"  Median polish hours:  {pol_med:.1f}h (threshold ≤ 8h)")
    console.print(f"Gate status: [bold]{gate['status']}[/bold] — {gate['reason']}")
    if not gate["passed"]:
        raise typer.Exit(1)


def register_benchmark_commands(root_app: typer.Typer) -> None:
    root_app.add_typer(benchmark_app, name="benchmark")
