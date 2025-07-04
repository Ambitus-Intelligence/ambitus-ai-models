from rich.console import Console
from rich.table import Table

class AgentInfoHandler:
    """Handles agent information display"""
    
    def __init__(self, console: Console):
        self.console = console
        
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
