from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.agents.company_research_agent import run_company_research_agent
from src.utils.validation import CompanyValidator
from src.utils.mcp_manager import MCPServerManager

router = APIRouter()

# Initialize utilities
company_validator = CompanyValidator()
mcp_manager = MCPServerManager()

class CompanyResearchRequest(BaseModel):
    company_name: str

class CompanyResearchResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None

@router.post("/", response_model=CompanyResearchResponse)
async def research_company(request: CompanyResearchRequest):
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
        return CompanyResearchResponse(
            success=False,
            error=agent_result["error"],
            raw_response=agent_result.get("raw_response")
        )
    
    # Validate the output
    validation_result = company_validator.validate(agent_result["data"])
    
    if not validation_result["valid"]:
        return CompanyResearchResponse(
            success=False,
            error=validation_result['error'],
            raw_response=agent_result.get("raw_response")
        )
    
    return CompanyResearchResponse(
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