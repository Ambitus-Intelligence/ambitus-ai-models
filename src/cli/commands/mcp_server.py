import click
import os
import sys
from rich.console import Console

console = Console()

@click.command(name="mcp")
@click.option('--host', default='localhost', help='Host to bind the MCP server')
@click.option('--port', default=8000, help='Port to bind the MCP server')
def mcp_command(host: str, port: int):
    """Start the MCP server"""
    try:
        from src.mcp.server import main as mcp_main
        
        console.print(f"[green]Starting MCP server on {host}:{port}[/green]")
        
        # Override the default host/port in the MCP server
        os.environ['MCP_HOST'] = host
        os.environ['MCP_PORT'] = str(port)
        
        mcp_main()
    except ImportError as e:
        console.print(f"[red]Error: MCP dependencies not installed or server module not found: {e}[/red]")
        console.print("[yellow]Make sure the MCP server module exists at src/mcp/server.py[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting MCP server: {e}[/red]")
        sys.exit(1)
