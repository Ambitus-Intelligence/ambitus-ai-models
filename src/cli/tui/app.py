import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.cli.tui.menus import MainMenuHandler
from src.cli.tui.server_status import ServerStatusHandler
from src.cli.tui.agent_info import AgentInfoHandler
from src.cli.tui.individual_agent_runner import IndividualAgentRunner

class AmbitusApp:
    """Terminal User Interface for Ambitus AI Models"""
    
    def __init__(self):
        self.console = Console()
        self.menu_handler = MainMenuHandler(self.console)
        self.server_status_handler = ServerStatusHandler(self.console)
        self.agent_info_handler = AgentInfoHandler(self.console)
        self.individual_agent_runner = IndividualAgentRunner(self.console)

        
    def run(self):
        """Main TUI loop"""
        while True:
            self.menu_handler.show_main_menu()
            choice = self.menu_handler.get_user_choice()
            
            # Clear console before transitioning to new section
            self.console.clear()
            
            if choice == "1":
                self.individual_agent_runner.run()
                # Clear console when returning from agent runner
                self.console.clear()
            elif choice == "2":
                self.server_status_handler.show_server_status()
                input("\nPress Enter to continue...")
                self.console.clear()
            elif choice == "3":
                self.agent_info_handler.show_agent_info()
                input("\nPress Enter to continue...")
                self.console.clear()
            elif choice == "4":
                self.console.clear()
                self.console.print("[yellow]Goodbye![/yellow]")
                break
            else:
                self.console.print("[red]Invalid choice! Please try again.[/red]")
                input("Press Enter to continue...")
                self.console.clear()