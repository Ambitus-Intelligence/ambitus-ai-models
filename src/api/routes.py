from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from routes import api_router
import sys
import os

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.mcp_manager import MCPServerManager

app = FastAPI(title="Ambitus AI Models API", version="0.0.1")

# Initialize utilities
mcp_manager = MCPServerManager()

# Include all API routes
app.include_router(api_router, prefix="/agents")

@app.get("/")
async def root():
    return {"message": "Ambitus AI Models API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    mcp_status = mcp_manager.is_server_running()
    return {
        "status": "healthy",
        "mcp_server_running": mcp_status
    }

@app.get("/mcp/status")
async def mcp_status():
    """Check MCP server status"""
    running = mcp_manager.is_server_running()
    return {
        "running": running,
        "server_url": mcp_manager.base_url
    }

@app.post("/mcp/start")
async def start_mcp_server():
    """Start the MCP server if not running"""
    result = mcp_manager.ensure_server_running()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
