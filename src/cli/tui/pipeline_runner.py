import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.pipeline.pipeline import run_linear_pipeline

class PipelineRunnerHandler:
    """Handles pipeline execution in TUI"""
    
    def __init__(self, console: Console):
        self.console = console
        
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
