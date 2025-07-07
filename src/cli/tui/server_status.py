from rich.console import Console
from rich.table import Table

class ServerStatusHandler:
    """Handles server status display"""
    
    def __init__(self, console: Console):
        self.console = console
        
    def show_server_status(self):
        """Display server status information"""
        self.console.print("\n[bold]Server Status[/bold]")
        
        # Check MCP server status
        mcp_status = self.check_server_status("http://localhost:8000/health")
        api_status = self.check_server_status("http://localhost:8001/health")
        
        status_table = Table(title="Server Status")
        status_table.add_column("Service", style="cyan")
        status_table.add_column("Status", style="yellow")
        status_table.add_column("URL", style="dim")
        
        status_table.add_row(
            "MCP Server",
            "[green]Running[/green]" if mcp_status else "[red]Stopped[/red]",
            "http://localhost:8000"
        )
        
        status_table.add_row(
            "API Server", 
            "[green]Running[/green]" if api_status else "[red]Stopped[/red]",
            "http://localhost:8001"
        )
        
        self.console.print(status_table)
        
        input("\nPress Enter to continue...")
        
    def check_server_status(self, url: str) -> bool:
        """Check if a server is running"""
        try:
            import requests
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
