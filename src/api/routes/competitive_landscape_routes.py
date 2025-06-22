from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.agents.competitive_landscape_agent import run_competitive_landscape_agent
from src.utils.validation import CompetitiveLandscapeValidator
from src.utils.mcp_manager import MCPServerManager
from src.utils.models import IndustryOpportunity, CompetitiveLandscapeResponse

router = APIRouter()

# Initialize utilities
competitive_landscape_validator = CompetitiveLandscapeValidator()
mcp_manager = MCPServerManager()

@router.post("/", response_model=CompetitiveLandscapeResponse)
async def analyze_competitive_landscape(request: IndustryOpportunity) -> CompetitiveLandscapeResponse:
    """
    Analyze competitive landscape using the CompetitiveLandscapeAgent.
    Automatically ensures MCP server is running.
    """
    # Ensure MCP server is running
    mcp_status = mcp_manager.ensure_server_running()
    if not mcp_status["success"]:
        raise HTTPException(
            status_code=503, 
            detail=f"MCP server not available: {mcp_status['message']}"
        ) 
    
    # Validate input
    input_data = request.model_dump()
    input_validation = competitive_landscape_validator.validate_input(input_data)
    
    if not input_validation["valid"]:
        return CompetitiveLandscapeResponse(
            success=False,
            error=f"Input validation failed: {input_validation['error']}"
        )
        
    # Run the agent
    agent_result = run_competitive_landscape_agent(input_data)
    
    if not agent_result["success"]:
        return CompetitiveLandscapeResponse(
            success=False,
            error=agent_result["error"],
            raw_response=agent_result.get("raw_response")
        )
    
    # Validate the output
    validation_result = competitive_landscape_validator.validate_output(agent_result["data"])
    
    if not validation_result["valid"]:
        return CompetitiveLandscapeResponse(
            success=False,
            error=validation_result['error'],
            raw_response=agent_result.get("raw_response")
        )
    
    return CompetitiveLandscapeResponse(
        success=True,
        data=validation_result["data"],
        raw_response=agent_result.get("raw_response")
    )

@router.get("/schema/input")
async def get_input_schema() -> Dict[str, Any]:
    """Get the input schema for competitive landscape analysis"""
    return competitive_landscape_validator.get_input_schema()

@router.get("/schema/output")
async def get_output_schema() -> Dict[str, Any]:
    """Get the output schema for competitive landscape analysis"""
    return competitive_landscape_validator.get_output_schema()