from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt

class MainMenuHandler:
    """Handles main menu display and user input"""
    
    def __init__(self, console: Console):
        self.console = console
        
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
