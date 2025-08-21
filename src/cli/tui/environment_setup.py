import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from pathlib import Path


class EnvironmentSetupHandler:
    """Handles environment variable setup and management"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_environment_setup(self):
        """Display environment setup interface"""
        while True:
            #self.console.clear()
            
            # Header
            header = Text("Ambitus", style="bold blue")
            header.append(" - Environment Setup", style="italic")
            
            # Check current status
            openai_key = os.getenv("OPENAI_API_KEY")
            
            # Create status table
            status_table = Table(show_header=True, header_style="bold magenta")
            status_table.add_column("Environment Variable", style="cyan", width=25)
            status_table.add_column("Status", justify="center", width=15)
            status_table.add_column("Value", style="dim", width=30)
            
            if openai_key:
                masked_key = f"{openai_key[:8]}...{openai_key[-4:]}" if len(openai_key) > 12 else "***"
                status_table.add_row("OPENAI_API_KEY", "✅ Set", masked_key)
            else:
                status_table.add_row("OPENAI_API_KEY", "❌ Not Set", "None")
            
            # Menu options
            menu_text = """
[bold cyan]Environment Setup Options[/bold cyan]

[1] Set OpenAI API Key
[2] Clear OpenAI API Key
[3] View Current Settings
[4] Back to Main Menu

Choose an option:"""
            
            self.console.print(Panel(header, style="blue"))
            self.console.print()
            self.console.print(Panel(status_table, title="Environment Status", style="green"))
            self.console.print()
            self.console.print(Panel(menu_text, title="Options", style="yellow"))
            
            choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                self._set_openai_key()
            elif choice == "2":
                self._clear_openai_key()
            elif choice == "3":
                self._view_current_settings()
            elif choice == "4":
                break
    
    def _set_openai_key(self):
        """Set the OpenAI API key"""
        self.console.print("\n[bold yellow]Set OpenAI API Key[/bold yellow]")
        self.console.print("[dim]Note: This will set the key for the current session only.[/dim]")
        self.console.print("[dim]For persistent storage, add it to your .env file.[/dim]\n")
        
        current_key = os.getenv("OPENAI_API_KEY")
        if current_key:
            self.console.print(f"[yellow]Current key: {current_key[:8]}...{current_key[-4:]}[/yellow]")
            if not Confirm.ask("Do you want to replace it?", default=False):
                return
        
        api_key = Prompt.ask("Enter your OpenAI API Key", password=True)
        
        if api_key and api_key.strip():
            # Basic validation
            if not api_key.startswith("sk-"):
                if not Confirm.ask("[yellow]API key doesn't start with 'sk-'. Continue anyway?[/yellow]", default=False):
                    return
            
            os.environ["OPENAI_API_KEY"] = api_key.strip()
            self.console.print("[green]✓ OpenAI API Key set successfully![/green]")
            
            # Offer to save to .env file
            if Confirm.ask("Would you like to save this to your .env file?", default=True):
                self._save_to_env_file("OPENAI_API_KEY", api_key.strip())
        else:
            self.console.print("[red]Invalid API key provided.[/red]")
        
        input("\nPress Enter to continue...")
    
    def _clear_openai_key(self):
        """Clear the OpenAI API key"""
        current_key = os.getenv("OPENAI_API_KEY")
        if not current_key:
            self.console.print("[yellow]No OpenAI API Key is currently set.[/yellow]")
            input("Press Enter to continue...")
            return
        
        if Confirm.ask("[red]Are you sure you want to clear the OpenAI API Key?[/red]", default=False):
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            self.console.print("[green]✓ OpenAI API Key cleared from current session.[/green]")
            
            if Confirm.ask("Would you like to remove it from your .env file as well?", default=False):
                self._remove_from_env_file("OPENAI_API_KEY")
        
        input("Press Enter to continue...")
    
    def _view_current_settings(self):
        """View current environment settings"""
        #self.console.clear()
        
        header = Text("Current Environment Settings", style="bold blue")
        self.console.print(Panel(header, style="blue"))
        
        # Create detailed table
        settings_table = Table(show_header=True, header_style="bold magenta")
        settings_table.add_column("Variable", style="cyan", width=20)
        settings_table.add_column("Status", width=15)
        settings_table.add_column("Source", width=15)
        settings_table.add_column("Value", style="dim")
        
        # Check OpenAI API Key
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            masked_key = f"{openai_key[:8]}...{openai_key[-4:]}" if len(openai_key) > 12 else "***"
            source = "Environment" if "OPENAI_API_KEY" in os.environ else "System"
            settings_table.add_row("OPENAI_API_KEY", "✅ Set", source, masked_key)
        else:
            settings_table.add_row("OPENAI_API_KEY", "❌ Not Set", "None", "None")
        
        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            settings_table.add_row(".env File", "✅ Exists", "File System", str(env_file.absolute()))
        else:
            settings_table.add_row(".env File", "❌ Not Found", "File System", "None")
        
        self.console.print(settings_table)
        input("\nPress Enter to continue...")
    
    def _save_to_env_file(self, key: str, value: str):
        """Save environment variable to .env file"""
        try:
            env_file = Path(".env")
            
            # Read existing content
            existing_lines = []
            if env_file.exists():
                existing_lines = env_file.read_text().splitlines()
            
            # Remove existing key if present
            existing_lines = [line for line in existing_lines if not line.startswith(f"{key}=")]
            
            # Add new key
            existing_lines.append(f"{key}={value}")
            
            # Write back to file
            env_file.write_text("\n".join(existing_lines) + "\n")
            
            self.console.print(f"[green]✓ Saved {key} to .env file[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Failed to save to .env file: {str(e)}[/red]")
    
    def _remove_from_env_file(self, key: str):
        """Remove environment variable from .env file"""
        try:
            env_file = Path(".env")
            
            if not env_file.exists():
                self.console.print("[yellow].env file does not exist.[/yellow]")
                return
            
            # Read existing content
            existing_lines = env_file.read_text().splitlines()
            
            # Remove the key
            new_lines = [line for line in existing_lines if not line.startswith(f"{key}=")]
            
            if len(new_lines) != len(existing_lines):
                env_file.write_text("\n".join(new_lines) + "\n")
                self.console.print(f"[green]✓ Removed {key} from .env file[/green]")
            else:
                self.console.print(f"[yellow]{key} was not found in .env file.[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Failed to update .env file: {str(e)}[/red]")
    
    @staticmethod
    def check_openai_key() -> bool:
        """Check if OpenAI API key is available"""
        return bool(os.getenv("OPENAI_API_KEY"))
