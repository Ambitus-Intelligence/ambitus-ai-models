import os
from fastapi import Request
from fastapi.responses import PlainTextResponse

try:
    from fastmcp import FastMCP
except ImportError as e:
    print(f"Error importing FastMCP: {e}")
    print("Please install FastMCP: pip install fastmcp")
    raise

try:
    from tools.ping_tool import ping_tool
    from tools.search_tool import search_tool
    from tools.citation_agent_tool import citation_agent
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some tools could not be imported: {e}")
    print("MCP server will start without these tools")
    TOOLS_AVAILABLE = False

# Create FastMCP server instance
mcp = FastMCP("ambitus-tools-mcp")

# Register tools only if they're available
if TOOLS_AVAILABLE:
    try:
        mcp.add_tool(ping_tool)
        mcp.add_tool(search_tool)
        mcp.add_tool(citation_agent)
    except Exception as e:
        print(f"Warning: Error registering tools: {e}")

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint for the MCP server.
    """
    return PlainTextResponse("OK")

def main():
    """Start the MCP server with SSE transport"""
    try:
        # Get host and port from environment variables
        host = os.getenv('MCP_HOST', 'localhost')
        port = int(os.getenv('MCP_PORT', '8000'))
        
        print(f"Starting MCP server on {host}:{port}")
        
        # Start SSE server
        mcp.run(transport="sse", host=host, port=port)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()
