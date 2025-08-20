from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt

from .keyboard_handler import KeyboardHandler, KeyCode, NavigationHandler

class MainMenuHandler:
    """Handles main menu display and user input with arrow key support"""
    
    def __init__(self, console: Console):
        self.console = console
        self.menu_items = [
            "Run Individual Agent",
            "Server Status", 
            "Agent Information",
            "Exit"
        ]
        self.navigator = NavigationHandler(self.menu_items)
        self.keyboard = KeyboardHandler()
        
    def show_main_menu(self):
        """Display the main menu with navigation support"""
        with self.keyboard:
            while True:
                self._display_menu()
                
                # Get key input
                key = self.keyboard.get_key()
                
                if key == KeyCode.UP.value:
                    self.navigator.move_up()
                elif key == KeyCode.DOWN.value:
                    self.navigator.move_down()
                elif key == KeyCode.ENTER.value:
                    return str(self.navigator.get_selected_index() + 1)
                elif key.lower() == 'q' or key == KeyCode.ESC.value:
                    return "4"
                elif key.isdigit() and 1 <= int(key) <= 4:
                    return key
    
    def _display_menu(self):
        """Display the menu with current selection highlighted"""
        self.console.clear()
        
        # Create header
        header = Text("Ambitus AI Models", style="bold blue")
        header.append(" - Market Research Automation Platform", style="italic")
        
        # Create menu with navigation indicators
        menu_text = Text("\n", style="bold cyan")
        menu_text.append("Main Menu\n\n", style="bold cyan")
        
        for i, item in enumerate(self.menu_items):
            if i == self.navigator.get_selected_index():
                menu_text.append(f"▶ [{i+1}] {item}\n", style="bold green")
            else:
                menu_text.append(f"  [{i+1}] {item}\n", style="white")
        
        menu_text.append("\nNavigation: ↑/↓ arrows, Enter to select, Q to quit", style="dim")
        
        layout = Layout()
        layout.split_column(
            Layout(Panel(header, style="blue"), size=3),
            Layout(Panel(menu_text, title="Options", style="green"))
        )
        
        self.console.print(layout)
        
    def get_user_choice(self) -> str:
        """Get user input choice (legacy method for compatibility)"""
        return self.show_main_menu()
