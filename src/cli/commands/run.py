import click
import sys
from rich.console import Console

from src.cli.tui.agent_runner import IndividualAgentRunner

console = Console()

@click.command(name="run")
def run_command():
    """Launch the Agent Runner directly"""
    try:
        # Clear console on startup
        console.clear()
        console.print("[bold blue]Starting Ambitus Intelligence Agent Runner...[/bold blue]")
        
        # Create and run the agent runner directly
        agent_runner = IndividualAgentRunner(console)
        agent_runner.run()
        
        # Clear console on normal exit
        console.clear()
    except KeyboardInterrupt:
        console.clear()
        console.print("\n[yellow]Agent Runner closed.[/yellow]")
    except Exception as e:
        console.clear()
        console.print(f"[red]Agent Runner Error: {e}[/red]")
        sys.exit(1)
