import click
import sys
import threading
import time
import signal
from rich.console import Console

console = Console()

@click.command(name="both")
@click.option('--mcp-host', default='localhost', help='Host for MCP server')
@click.option('--mcp-port', default=8000, help='Port for MCP server')
@click.option('--api-host', default='localhost', help='Host for API server')
@click.option('--api-port', default=8001, help='Port for API server')
@click.option('--reload', is_flag=True, help='Enable auto-reload for API server')
def both_command(mcp_host: str, mcp_port: int, api_host: str, api_port: int, reload: bool):
    """Start both MCP and API servers concurrently"""
    
    def start_mcp():
        try:
            import os
            from src.mcp.server import main as mcp_main
            
            console.print(f"[green]Starting MCP server on {mcp_host}:{mcp_port}[/green]")
            
            # Override the default host/port in the MCP server
            os.environ['MCP_HOST'] = mcp_host
            os.environ['MCP_PORT'] = str(mcp_port)
            
            mcp_main()
        except ImportError as e:
            console.print(f"[red]Error: MCP dependencies not installed or server module not found: {e}[/red]")
        except Exception as e:
            console.print(f"[red]Error starting MCP server: {e}[/red]")
    
    def start_api():
        try:
            import uvicorn
            from src.api.router import app
            
            console.print(f"[green]Starting FastAPI server on {api_host}:{api_port}[/green]")
            if reload:
                console.print("[yellow]Auto-reload enabled for API server[/yellow]")
            
            uvicorn.run(
                "src.api.router:app",
                host=api_host,
                port=api_port,
                reload=reload
            )
        except ImportError:
            console.print("[red]Error: FastAPI dependencies not installed[/red]")
        except Exception as e:
            console.print(f"[red]Error starting API server: {e}[/red]")
    
    # Start both servers in separate threads
    mcp_thread = threading.Thread(target=start_mcp, daemon=True)
    api_thread = threading.Thread(target=start_api, daemon=True)
    
    console.print("[blue]Starting both MCP and API servers...[/blue]")
    
    try:
        mcp_thread.start()
        time.sleep(1)  # Give MCP server a moment to start
        api_thread.start()
        
        console.print("[green]Both servers started successfully![/green]")
        console.print("[yellow]Press Ctrl+C to stop both servers[/yellow]")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down servers...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error running servers: {e}[/red]")
        sys.exit(1)
