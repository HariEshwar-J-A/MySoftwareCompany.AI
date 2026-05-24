"""Typer CLI: msc / mscai entry points."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from msc import __version__
import msc.config as msc_config
from msc.config import MSCConfig
from msc.loader.catalog import get_agent, list_agents
from msc.loader.org_template import list_org_templates, load_org_template
from msc.review.deliverable import DeliverableCheckError
from msc.runtime.dry_run import format_report, run_dry_run
from msc.runtime.llm_config import llm_credentials_ready
from msc.runtime.org_model import workspace_dir_for_org

app = typer.Typer(help="MySoftwareCompany.AI — run AI software agencies.", no_args_is_help=True)
orgs_app = typer.Typer(help="Org templates.")
agents_app = typer.Typer(help="agency-agents personas.")
app.add_typer(orgs_app, name="orgs")
app.add_typer(agents_app, name="agents")
console = Console()
stderr_console = Console(file=sys.stderr)


@app.command("version")
def version_cmd() -> None:
    """Print package version."""
    console.print(f"mscai {__version__}")


@app.command()
def init(force: bool = typer.Option(False, "--force")) -> None:
    """Write ~/.msc/config.yaml."""
    path = msc_config.DEFAULT_CONFIG_PATH
    if path.exists() and not force:
        console.print(f"Config already exists: {path}")
        raise typer.Exit(0)
    console.print(f"Wrote config: {MSCConfig().save(path)}")


@orgs_app.command("list")
def orgs_list() -> None:
    """List org templates (OSS + entitled premium packs)."""
    templates = list_org_templates(MSCConfig.load())
    if not templates:
        console.print("[yellow]No org templates found.[/yellow]")
        raise typer.Exit(0)
    table = Table(title="Org templates")
    for col in ("Name", "Mode", "License", "Description"):
        table.add_column(col)
    for t in templates:
        d = t.description[:60] + ("…" if len(t.description) > 60 else "")
        table.add_row(t.name, t.mode, t.license, d)
    console.print(table)


@agents_app.command("list")
def agents_list(division: Optional[str] = typer.Option(None, "--division")) -> None:
    """List agency-agents personas."""
    cfg = MSCConfig.load()
    agents = list_agents(division=division, agents_root=cfg.agency_agents_root)
    if not agents:
        console.print(
            f"[yellow]No agents under {cfg.agency_agents_root}. Run make vendor-sync.[/yellow]"
        )
        raise typer.Exit(0)
    table = Table(title="Agents")
    for col in ("Slug", "Division", "Name"):
        table.add_column(col)
    for a in agents:
        table.add_row(a.slug, a.division, a.name)
    console.print(table)


@agents_app.command("show")
def agents_show(slug: str) -> None:
    """Show one agent persona."""
    cfg = MSCConfig.load()
    agent = get_agent(slug, agents_root=cfg.agency_agents_root)
    if not agent:
        console.print(f"[red]Agent not found:[/red] {slug}")
        raise typer.Exit(1)
    console.print(
        f"[bold]{agent.name}[/bold] ({agent.slug})\nDivision: {agent.division}\nPath: {agent.path}"
    )
    if agent.description:
        console.print(f"\n{agent.description}")


@app.command()
def run(
    idea: str,
    org: Optional[str] = typer.Option(None, "--org"),
    budget: Optional[float] = typer.Option(None, "--budget"),
    rounds: Optional[int] = typer.Option(None, "--rounds"),
    no_human_review: bool = typer.Option(
        False,
        "--no-human-review",
        help="Disable human review (stderr warning; sets no_human_review in workspace metadata).",
    ),
) -> None:
    """Run an org against a project idea."""
    import os
    from pathlib import Path

    cfg = MSCConfig.load()
    org_name = org or cfg.default_org
    template = load_org_template(org_name, cfg)
    # MSC_BENCHMARK_WORKSPACE lets the benchmark runner redirect output to
    # benchmarks/runs/<id>/workspace instead of the default workspace/<org>/ path.
    if _bm_ws := os.environ.get("MSC_BENCHMARK_WORKSPACE", "").strip():
        workspace = Path(_bm_ws)
    else:
        workspace = workspace_dir_for_org(template.name, cfg.workspace_root)
    workspace.mkdir(parents=True, exist_ok=True)
    if no_human_review:
        stderr_console.print(
            "[bold red]WARNING: Human review gate disabled. Do not use for client deliverables.[/bold red]"
        )
        msc_dir = workspace / ".msc"
        msc_dir.mkdir(parents=True, exist_ok=True)
        meta_path = msc_dir / "metadata.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        meta["no_human_review"] = True
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    report = run_dry_run(org_name, cfg)
    if not report.ok:
        console.print(format_report(report))
        raise typer.Exit(1)

    try:
        import metagpt  # noqa: F401
    except ImportError:
        console.print("[yellow]MetaGPT not installed — dry-run only.[/yellow]")
        console.print("Install with: make install-dev")
        console.print(format_report(report))
        raise typer.Exit(0)

    ready, hint = llm_credentials_ready()
    if not ready:
        console.print(f"[yellow]{hint}[/yellow]")
        console.print(format_report(report))
        raise typer.Exit(0)

    n_rounds = rounds if rounds is not None else cfg.default_rounds
    invest = budget if budget is not None else template.budget_default
    console.print(
        f"[bold]Running org '{template.name}'[/bold] "
        f"(budget≈${invest:.0f}, rounds={n_rounds}) → {workspace.resolve()}"
    )
    from msc.runtime.runner import run_org_project

    try:
        company = asyncio.run(
            run_org_project(
                idea,
                template,
                cfg,
                budget=budget,
                rounds=rounds,
                no_human_review=no_human_review,
                workspace_override=workspace if _bm_ws else None,
            )
        )
    except DeliverableCheckError as exc:
        console.print("[red]Run finished but deliverable check failed:[/red]")
        for msg in exc.report.errors:
            console.print(f"  • {msg}")
        for msg in exc.report.warnings:
            console.print(f"  [yellow]• {msg}[/yellow]")
        raise typer.Exit(1) from exc
    except Exception as exc:
        console.print(f"[red]Run failed:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[green]Run finished.[/green] Workspace: {company.workspace.resolve()}")
    raise typer.Exit(0)


@app.command("resume")
def resume(
    org: Optional[str] = typer.Option(None, "--org", help="Org template name (for workspace path)"),
    rounds: Optional[int] = typer.Option(None, "--rounds", help="Additional MetaGPT rounds"),
    idea: str = typer.Option("", "--idea", help="Optional follow-up instruction"),
) -> None:
    """Resume a serialized team from workspace/.msc/team/."""
    cfg = MSCConfig.load()
    org_name = org or cfg.default_org
    workspace = workspace_dir_for_org(org_name, cfg.workspace_root)
    from msc.runtime.serialize import has_saved_team, resume_team

    if not has_saved_team(workspace):
        console.print(f"[red]No saved team at {workspace / '.msc/team/team.json'}[/red]")
        console.print("Run `msc run` first to create a serialized team.")
        raise typer.Exit(1)

    ready, hint = llm_credentials_ready()
    if not ready:
        console.print(f"[yellow]{hint}[/yellow]")
        raise typer.Exit(0)

    n_rounds = rounds if rounds is not None else cfg.default_rounds
    console.print(
        f"[bold]Resuming org '{org_name}'[/bold] (rounds={n_rounds}) → {workspace.resolve()}"
    )
    try:
        company = asyncio.run(resume_team(workspace, n_round=n_rounds, idea=idea))
    except Exception as exc:
        console.print(f"[red]Resume failed:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]Resume finished.[/green] Workspace: {company.workspace.resolve()}")
    raise typer.Exit(0)


@app.command("dry-run")
def dry_run(org: Optional[str] = typer.Option(None, "--org", help="Org template name")) -> None:
    """Validate org wiring without LLM calls."""
    cfg = MSCConfig.load()
    report = run_dry_run(org or cfg.default_org, cfg)
    console.print(format_report(report))
    raise typer.Exit(0 if report.ok else 1)


from msc.benchmarks.cli import register_benchmark_commands  # noqa: E402
from msc.marketplace.cli import marketplace_app  # noqa: E402

register_benchmark_commands(app)
app.add_typer(marketplace_app, name="marketplace")
