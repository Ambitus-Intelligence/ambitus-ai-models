import click
import json
import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.json import JSON

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.pipeline.pipeline import run_linear_pipeline

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def main():
    """
    Ambitus AI Models - Market Research Automation Platform
    
    A comprehensive CLI tool for running AI-powered market research agents.
    """
    pass

@main.command()
@click.option('--host', default='localhost', help='Host to bind the API server')
@click.option('--port', default=8001, help='Port to bind the API server')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def api(host: str, port: int, reload: bool):
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

@main.command()
@click.option('--host', default='localhost', help='Host to bind the MCP server')
@click.option('--port', default=8000, help='Port to bind the MCP server')
def mcp(host: str, port: int):
    """Start the MCP server"""
    try:
        # Use absolute import from project root
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

@main.command()
@click.argument('company_name')
@click.option('--domain', help='Specific domain to analyze (optional)')
@click.option('--output', '-o', help='Output file path for results')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'markdown', 'pdf']), 
              help='Output format')
def pipeline(company_name: str, domain: Optional[str], output: Optional[str], output_format: str):
    """Run the complete market research pipeline"""
    
    console.print(f"[blue]Starting market research pipeline for: {company_name}[/blue]")
    
    if domain:
        console.print(f"[blue]Analyzing domain: {domain}[/blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running pipeline...", total=None)
        
        try:
            # Run the pipeline
            result = run_linear_pipeline(company_name, domain)
            
            if result.get('success'):
                console.print("[green]✓ Pipeline completed successfully![/green]")
                
                # Save output if specified
                if output:
                    output_path = Path(output)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if output_format == 'json':
                        with open(output_path, 'w') as f:
                            json.dump(result, f, indent=2)
                    elif output_format == 'markdown':
                        # Extract markdown content if available
                        content = result.get('pdf_content', json.dumps(result, indent=2))
                        with open(output_path, 'w') as f:
                            f.write(content)
                    
                    console.print(f"[green]Results saved to: {output_path}[/green]")
                else:
                    # Display results in console
                    console.print("\n[bold]Pipeline Results:[/bold]")
                    console.print(JSON(json.dumps(result, indent=2)))
                    
            else:
                console.print("[red]✗ Pipeline failed![/red]")
                console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
                sys.exit(1)
                
        except Exception as e:
            console.print(f"[red]✗ Pipeline error: {e}[/red]")
            sys.exit(1)

@main.command()
def tui():
    """Launch the Terminal User Interface"""
    try:
        app = AmbitusApp()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]TUI Error: {e}[/red]")
        sys.exit(1)

class AmbitusApp:
    """Terminal User Interface for Ambitus AI Models"""
    
    def __init__(self):
        self.console = Console()
        self.agents = [
            "Company Research Agent",
            "Industry Analysis Agent", 
            "Market Data Agent",
            "Competitive Landscape Agent",
            "Market Gap Analysis Agent",
            "Opportunity Agent",
            "Report Synthesis Agent"
        ]
        
    def run(self):
        """Main TUI loop"""
        while True:
            self.show_main_menu()
            choice = self.get_user_choice()
            
            if choice == "1":
                self.run_individual_agent()
            elif choice == "2":
                self.run_full_pipeline()
            elif choice == "3":
                self.show_server_status()
            elif choice == "4":
                self.show_agent_info()
            elif choice == "5":
                break
            else:
                self.console.print("[red]Invalid choice! Please try again.[/red]")
                
    def show_main_menu(self):
        """Display the main menu"""
        self.console.clear()
        
        # Create header
        header = Text("Ambitus AI Models", style="bold blue")
        header.append(" - Market Research Automation Platform", style="italic")
        
        # Create menu panel
        menu_text = """
[bold cyan]Main Menu[/bold cyan]

[1] Run Individual Agent
[2] Run Full Pipeline
[3] Server Status
[4] Agent Information
[5] Exit

Choose an option:"""
        
        layout = Layout()
        layout.split_column(
            Layout(Panel(header, style="blue"), size=3),
            Layout(Panel(menu_text, title="Options", style="green"))
        )
        
        self.console.print(layout)
        
    def get_user_choice(self) -> str:
        """Get user input choice"""
        return Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        
    def run_individual_agent(self):
        """Interface for running individual agents"""
        self.console.print("\n[bold]Individual Agent Runner[/bold]")
        
        # Show available agents
        table = Table(title="Available Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Agent Name", style="green")
        table.add_column("Status", style="yellow")
        
        for i, agent in enumerate(self.agents, 1):
            table.add_row(str(i), agent, "Available")
            
        self.console.print(table)
        
        agent_id = Prompt.ask("Select agent ID", choices=[str(i) for i in range(1, len(self.agents) + 1)])
        selected_agent = self.agents[int(agent_id) - 1]
        
        self.console.print(f"\n[blue]Selected: {selected_agent}[/blue]")
        self.console.print("[yellow]Individual agent execution not yet implemented.[/yellow]")
        self.console.print("[dim]This feature will be available in future versions.[/dim]")
        
        input("\nPress Enter to continue...")
        
    def run_full_pipeline(self):
        """Interface for running the full pipeline"""
        self.console.print("\n[bold]Full Pipeline Runner[/bold]")
        
        company_name = Prompt.ask("Enter company name")
        domain = Prompt.ask("Enter domain (optional, press Enter to skip)", default="")
        
        if not domain:
            domain = None
            
        save_output = Confirm.ask("Save output to file?", default=True)
        output_path = None
        
        if save_output:
            output_path = Prompt.ask("Enter output file path", default=f"output/{company_name}_research.json")
            
        self.console.print(f"\n[blue]Starting pipeline for: {company_name}[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Running pipeline...", total=None)
            
            try:
                result = run_linear_pipeline(company_name, domain)
                
                if result.get('success'):
                    self.console.print("[green]✓ Pipeline completed successfully![/green]")
                    
                    if output_path:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        with open(output_path, 'w') as f:
                            json.dump(result, f, indent=2)
                        self.console.print(f"[green]Results saved to: {output_path}[/green]")
                    
                    # Show summary
                    self.show_pipeline_summary(result)
                else:
                    self.console.print("[red]✗ Pipeline failed![/red]")
                    self.console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
                    
            except Exception as e:
                self.console.print(f"[red]Pipeline error: {e}[/red]")
                
        input("\nPress Enter to continue...")
        
    def show_pipeline_summary(self, result: dict):
        """Display pipeline results summary"""
        summary_panel = Panel(
            f"""[bold green]Pipeline Summary[/bold green]

[bold]Report Title:[/bold] {result.get('report_title', 'N/A')}
[bold]Generated At:[/bold] {result.get('generated_at', 'N/A')}
[bold]Status:[/bold] {'✓ Success' if result.get('success') else '✗ Failed'}
[bold]Placeholder:[/bold] {result.get('placeholder', 'N/A')}
""",
            title="Results",
            style="green"
        )
        
        self.console.print(summary_panel)
        
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
            
    def show_agent_info(self):
        """Display agent information"""
        self.console.print("\n[bold]Agent Information[/bold]")
        
        info_table = Table(title="Agent Details")
        info_table.add_column("Agent", style="cyan")
        info_table.add_column("Purpose", style="green")
        info_table.add_column("Status", style="yellow")
        
        agent_info = {
            "Company Research Agent": "Collect foundational company data",
            "Industry Analysis Agent": "Identify expansion domains",
            "Market Data Agent": "Fetch quantitative market metrics",
            "Competitive Landscape Agent": "Map competitors and offerings",
            "Market Gap Analysis Agent": "Detect unmet market needs",
            "Opportunity Agent": "Generate growth opportunities",
            "Report Synthesis Agent": "Compile final research report"
        }
        
        for agent, purpose in agent_info.items():
            info_table.add_row(agent, purpose, "Available")
            
        self.console.print(info_table)
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
