from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.agents.company_research_agent import run_company_research_agent
from src.utils.validation import CompanyValidator
from src.utils.mcp_manager import MCPServerManager
from src.utils.models import CompanyResearchRequest, CompanyResponse

router = APIRouter()

# Initialize utilities
company_validator = CompanyValidator()
mcp_manager = MCPServerManager()

@router.post("/", response_model=CompanyResponse)
async def research_company(request: CompanyResearchRequest) -> CompanyResponse:
    """
    Research a company using the CompanyResearchAgent.
    Automatically ensures MCP server is running.
    """
    # Ensure MCP server is running
    mcp_status = mcp_manager.ensure_server_running()
    if not mcp_status["success"]:
        raise HTTPException(
            status_code=503, 
            detail=f"MCP server not available: {mcp_status['message']}"
        ) 
        
    # Run the agent
    agent_result = run_company_research_agent(request.company_name)
    
    if not agent_result["success"]:
        return CompanyResponse(
            success=False,
            error=agent_result["error"],
            raw_response=agent_result.get("raw_response")
        )
    
    # Validate the output
    validation_result = company_validator.validate(agent_result["data"])
    
    if not validation_result["valid"]:
        return CompanyResponse(
            success=False,
            error=validation_result['error'],
            raw_response=agent_result.get("raw_response")
        )
    
    return CompanyResponse(
        success=True,
        data=validation_result["data"],
        raw_response=agent_result.get("raw_response")
    )

@router.get("/schema/input")
async def get_input_schema() -> Dict[str, Any]:
    """Get the input schema for company research (company name string)"""
    return {
        "type": "object",
        "properties": {
            "company_name": {
                "type": "string",
                "description": "Name of the company to research"
            }
        },
        "required": ["company_name"]
    }

@router.get("/schema/output")
async def get_output_schema() -> Dict[str, Any]:
    """Get the output schema for company research"""
    return company_validator.get_schema()