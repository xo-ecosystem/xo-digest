#!/usr/bin/env python3
import os
from pathlib import Path

import typer
import yaml

app = typer.Typer(name="xo-cli")
# Nested command group for pulse‑related actions
pulse = typer.Typer(help="Pulse‑related commands")
app.add_typer(pulse, name="pulse")

# ------------------------------------------------------------------
# Pulse sub‑commands
# ------------------------------------------------------------------
FAB_CMD = "fab -f ./fabfile.py"


@pulse.command("new")
def pulse_new(slug: str):
    """Create a new pulse entry"""
    typer.echo(f"🆕 Generating new pulse: {slug}")
    os.system(f"{FAB_CMD} pulse.new {slug}")


@pulse.command("publish")
def pulse_publish(slug: str):
    """Sign and sync a pulse"""
    typer.echo(f"🔏 Signing: {slug}")
    os.system(f"{FAB_CMD} vault.sign {slug}")
    typer.echo(f"🌐 Syncing: {slug}")
    os.system(f"{FAB_CMD} pulse.sync")


@pulse.command("sync")
def pulse_sync():
    """Sync pulses via Fabric"""
    typer.echo("🔁 Syncing pulses via Fabric…")
    os.system(f"{FAB_CMD} pulse.sync")


@pulse.command("sign")
def pulse_sign(slug: str):
    """Sign a pulse without syncing"""
    typer.echo(f"🔏 Signing pulse: {slug}")
    os.system(f"{FAB_CMD} vault.sign {slug}")


@pulse.command("archive-all")
def pulse_archive_all():
    """Archive all pulses"""
    typer.echo("📦 Archiving all pulses…")
    os.system(f"{FAB_CMD} pulse.archive-all")


def load_config(profile: str = "default"):
    path = Path(".xo-cli.yml")
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text())
    return data.get(profile, {})


@app.command()
def dev(profile: str = typer.Option("default", "--profile")):
    config = load_config(profile)
    typer.echo(f"🔁 Dev loop started with profile: {profile}")
    typer.echo(f"⚙️  Loaded config: {config}")


@app.command()
def publish():
    typer.echo("📡 Publishing...")


@app.command()
def test():
    import subprocess

    subprocess.run(["python", "-m", "unittest", "discover", "tests/"])


if __name__ == "__main__":
    app()
