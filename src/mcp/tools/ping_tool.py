from typing import Any, Dict

def ping_tool(message: str = "ping") -> Dict[str, Any]:
    """
    Echo back any input message - useful for testing connectivity
    
    Args:
        message: The message to echo back
        
    Returns:
        Dict containing the echoed message
    """
    return {
        "echo": message,
        "status": "success", 
        "tool": "ping"
    }

# Add tool metadata
ping_tool.__name__ = "ping"
ping_tool.__doc__ = "Echo back any input message - useful for testing connectivity"
