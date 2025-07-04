import click
import sys
from rich.console import Console

from src.cli.tui.app import AmbitusApp

console = Console()

@click.command(name="tui")
def tui_command():
    """Launch the Terminal User Interface"""
    try:
        app = AmbitusApp()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]TUI Error: {e}[/red]")
        sys.exit(1)
