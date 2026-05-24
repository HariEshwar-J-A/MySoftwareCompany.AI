# Copyright (c) 2026 MySoftwareCompany.AI
# SPDX-License-Identifier: BUSL-1.1

"""Marketplace CLI: license login and premium org pack listing."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from msc.entitlements.keys import load_stored_license, save_stored_license, verify_license_token
from msc.marketplace.loader import list_premium_pack_ids, premium_orgs_dir

console = Console()
marketplace_app = typer.Typer(
    help="Marketplace licenses and premium org packs.",
    no_args_is_help=True,
)


@marketplace_app.command("login")
def marketplace_login(key: str = typer.Argument(..., help="MSC1 license token")) -> None:
    """Verify and store a marketplace license key."""
    try:
        payload = verify_license_token(key)
    except ValueError as exc:
        console.print(f"[red]Invalid license:[/red] {exc}")
        raise typer.Exit(1) from exc
    path = save_stored_license(key, payload)
    packs = ", ".join(payload.entitled_packs) or "(none)"
    console.print(f"[green]License saved[/green] → {path}")
    console.print(f"Customer: {payload.customer_id}  Tier: {payload.tier}  Packs: {packs}")


@marketplace_app.command("orgs")
def marketplace_orgs() -> None:
    """List premium org packs and entitlement status."""
    pack_ids = list_premium_pack_ids()
    if not pack_ids:
        console.print(f"[yellow]No premium packs under {premium_orgs_dir()}[/yellow]")
        raise typer.Exit(0)
    stored = load_stored_license()
    entitled: set[str] = set()
    if stored:
        _, payload = stored
        entitled = set(payload.entitled_packs)
    table = Table(title="Premium org packs")
    for col in ("Pack ID", "Status"):
        table.add_column(col)
    for pack_id in pack_ids:
        status = "[green]entitled[/green]" if pack_id in entitled else "[dim]locked[/dim]"
        table.add_row(pack_id, status)
    console.print(table)
