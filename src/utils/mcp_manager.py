import subprocess
import requests
import time
import os
from typing import Dict, Any

class MCPServerManager:
    """Manager for FastMCP server operations"""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.health_endpoint = f"{self.base_url}/health"
        
    def is_server_running(self) -> bool:
        """Check if the MCP server is running"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_server(self) -> Dict[str, Any]:
        """Start the MCP server if not already running"""
        if self.is_server_running():
            return {
                "success": True,
                "message": "MCP server is already running",
                "action": "none"
            }
        
        try:
            # Get the project root directory
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            server_script = os.path.join(project_root, "src", "mcp", "server.py")
            
            # Start the server in a subprocess
            process = subprocess.Popen(
                ["python", server_script],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a bit for the server to start
            time.sleep(3)
            
            # Check if it's running
            if self.is_server_running():
                return {
                    "success": True,
                    "message": "MCP server started successfully",
                    "action": "started",
                    "pid": process.pid
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to start MCP server",
                    "action": "failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting MCP server: {str(e)}",
                "action": "error"
            }
    
    def ensure_server_running(self) -> Dict[str, Any]:
        """Ensure the MCP server is running, start if necessary"""
        return self.start_server()
