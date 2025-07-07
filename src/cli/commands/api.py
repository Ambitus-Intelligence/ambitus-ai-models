import click
import sys
from rich.console import Console

console = Console()

@click.command(name="api")
@click.option('--host', default='localhost', help='Host to bind the API server')
@click.option('--port', default=8001, help='Port to bind the API server')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def api_command(host: str, port: int, reload: bool):
    """Start the FastAPI server"""
    try:
        import uvicorn
        from src.api.router import app
        
        console.print(f"[green]Starting FastAPI server on {host}:{port}[/green]")
        if reload:
            console.print("[yellow]Auto-reload enabled[/yellow]")
        
        uvicorn.run(
            "src.api.router:app",
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        console.print("[red]Error: FastAPI dependencies not installed[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error starting API server: {e}[/red]")
        sys.exit(1)
