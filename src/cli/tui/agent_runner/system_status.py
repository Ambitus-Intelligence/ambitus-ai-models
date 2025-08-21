import os
import subprocess
import requests
from typing import Dict, Any
from rich.console import Console
from rich.text import Text


class SystemStatusHandler:
    """Handles system status checking and management"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def check_mcp_server_status(self) -> Dict[str, Any]:
        """Check if MCP server is running"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                return {
                    "running": True,
                    "status": "✅ Running",
                    "message": "MCP Server is running on port 8000"
                }
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.RequestException):
            pass
        
        return {
            "running": False,
            "status": "❌ Not Running",
            "message": "MCP Server is not responding"
        }
    
    def check_openai_key_status(self) -> Dict[str, Any]:
        """Check if OpenAI API key is available"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key and api_key.strip():
            masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            return {
                "available": True,
                "status": "✅ Available",
                "value": masked_key,
                "message": "OpenAI API Key is set"
            }
        else:
            return {
                "available": False,
                "status": "❌ Not Set",
                "value": "None",
                "message": "OpenAI API Key is not configured"
            }
    
    def start_mcp_server(self) -> Dict[str, Any]:
        """Attempt to start MCP server"""
        try:
            # This is a placeholder - implement based on your MCP server startup process
            self.console.print("[yellow]Attempting to start MCP server...[/yellow]")
            
            # Check if server is already running
            current_status = self.check_mcp_server_status()
            if current_status["running"]:
                return {
                    "success": True,
                    "message": "MCP server is already running"
                }
            
            # Example command - adjust based on your setup
            # subprocess.Popen(["python", "-m", "your_mcp_server"], 
            #                  stdout=subprocess.DEVNULL, 
            #                  stderr=subprocess.DEVNULL)
            
            return {
                "success": False,
                "message": "MCP server startup not implemented yet. Please start manually."
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to start MCP server: {str(e)}"
            }
    
    def stop_mcp_server(self) -> Dict[str, Any]:
        """Attempt to stop MCP server"""
        try:
            # Check if server is running first
            current_status = self.check_mcp_server_status()
            if not current_status["running"]:
                return {
                    "success": True,
                    "message": "MCP server is not running"
                }
            
            # Send shutdown request
            response = requests.post("http://localhost:8000/shutdown", timeout=5)
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "MCP server shutdown request sent successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"MCP server responded with status code: {response.status_code}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": True,
                "message": "MCP server appears to be stopped (connection refused)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to stop MCP server: {str(e)}"
            }
    
    def get_status_indicators(self) -> Text:
        """Get formatted status indicators for display"""
        mcp_status = self.check_mcp_server_status()
        openai_status = self.check_openai_key_status()
        
        status_text = Text()
        
        # MCP Server status
        status_text.append("MCP: ", style="bold")
        if mcp_status["running"]:
            status_text.append("✅", style="green")
        else:
            status_text.append("❌", style="red")
        
        status_text.append("  ")
        
        # OpenAI API Key status
        status_text.append("API: ", style="bold")
        if openai_status["available"]:
            status_text.append("✅", style="green")
        else:
            status_text.append("❌", style="red")
        
        return status_text
    
    def get_detailed_status_text(self) -> Text:
        """Get detailed status information"""
        mcp_status = self.check_mcp_server_status()
        openai_status = self.check_openai_key_status()
        
        status_text = Text()
        
        # MCP Server
        status_text.append("🖥️  MCP: ", style="bold")
        if mcp_status["running"]:
            status_text.append("✅ Running\n", style="green")
        else:
            status_text.append("❌ Stopped\n", style="red")
        
        # OpenAI API Key
        status_text.append("🔑 API: ", style="bold")
        if openai_status["available"]:
            status_text.append("✅ Set\n", style="green")
        else:
            status_text.append("❌ Missing\n", style="red")
        
        # Control instructions
        status_text.append("\n[M] Toggle MCP\n[K] Manage API Key", style="yellow")
        
        return status_text
