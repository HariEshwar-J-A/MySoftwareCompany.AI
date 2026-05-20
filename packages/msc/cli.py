"""Typer CLI: msc / mscai entry points."""

from __future__ import annotations

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
from msc.runtime.dry_run import format_report, run_dry_run

app = typer.Typer(help="MySoftwareCompany.AI — run AI software agencies.", no_args_is_help=True)
orgs_app = typer.Typer(help="Org templates.")
agents_app = typer.Typer(help="agency-agents personas.")
app.add_typer(orgs_app, name="orgs")
app.add_typer(agents_app, name="agents")
console = Console()
stderr_console = Console(file=sys.stderr)


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
    """List OSS org templates."""
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
        console.print(f"[yellow]No agents under {cfg.agency_agents_root}. Run make vendor-sync.[/yellow]")
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
    console.print(f"[bold]{agent.name}[/bold] ({agent.slug})\nDivision: {agent.division}\nPath: {agent.path}")
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
    cfg = MSCConfig.load()
    org_name = org or cfg.default_org
    template = load_org_template(org_name, cfg)
    workspace = cfg.workspace_root / template.name
    workspace.mkdir(parents=True, exist_ok=True)
    if no_human_review:
        stderr_console.print("[bold red]WARNING: Human review gate disabled. Do not use for client deliverables.[/bold red]")
        meta_path = workspace / "metadata.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        meta["no_human_review"] = True
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    try:
        import metagpt  # noqa: F401
    except ImportError:
        console.print("[yellow]MetaGPT not installed — running dry-run validation only.[/yellow]")
        console.print("Install with: make install-dev")
        report = run_dry_run(org_name, cfg)
        console.print(format_report(report))
        raise typer.Exit(0 if report.ok else 1)

    console.print(
        f"[yellow]Full LLM run for org '{template.name}' requires API keys in ~/.msc/config.yaml.[/yellow]"
    )
    console.print("Validating wiring via dry-run first…")
    report = run_dry_run(org_name, cfg)
    console.print(format_report(report))
    raise typer.Exit(0 if report.ok else 1)


@app.command("dry-run")
def dry_run(org: Optional[str] = typer.Option(None, "--org")) -> None:
    """Validate org wiring without LLM calls."""
    cfg = MSCConfig.load()
    report = run_dry_run(org or cfg.default_org, cfg)
    console.print(format_report(report))
    raise typer.Exit(0 if report.ok else 1)


@app.callback()
def main(version: bool = typer.Option(False, "--version", "-V")) -> None:
    if version:
        console.print(f"mscai {__version__}")
        raise typer.Exit(0)


from msc.benchmarks.cli import register_benchmark_commands  # noqa: E402

register_benchmark_commands(app)
