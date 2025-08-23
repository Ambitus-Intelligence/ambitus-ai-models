import click
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands.api_server import api_command
from src.cli.commands.both import both_command
from src.cli.commands.mcp_server import mcp_command
from src.cli.commands.tui import tui_command
from src.cli.commands.run import run_command

@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    Ambitus AI Models - Market Research Automation Platform
    
    A comprehensive CLI tool for running AI-powered market research agents.
    """
    pass

# Register commands
main.add_command(api_command)
main.add_command(both_command)
main.add_command(mcp_command)
main.add_command(tui_command)
main.add_command(run_command)

if __name__ == "__main__":
    main()
