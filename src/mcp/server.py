from fastmcp import FastMCP
from tools.ping_tool import ping_tool
from tools.search_tool import search_tool
from fastapi import Request
from fastapi.responses import PlainTextResponse

# Create FastMCP server instance
mcp = FastMCP("ambitus-tools-mcp")

# Register the ping tool function
mcp.add_tool(ping_tool)
# Register the search tool function
mcp.add_tool(search_tool)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint for the MCP server.
    """
    return PlainTextResponse("OK")

def main():
    """Start the MCP server with SSE transport"""
    try:
        # Start SSE server on localhost:8000
        mcp.run(transport="sse", host="localhost", port=8000)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()
