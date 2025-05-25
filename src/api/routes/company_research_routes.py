from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.agents.company_research_agent import run_company_research_agent
#from src.utils.validation import CompanyValidator
from src.utils.mcp_manager import MCPServerManager

router = APIRouter()

# Initialize utilities
#company_validator = CompanyValidator()
mcp_manager = MCPServerManager()

class CompanyResearchRequest(BaseModel):
    company_name: str

class CompanyResearchResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    #validation: Optional[Dict[str, Any]] = None
    #error: Optional[str] = None

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
            mcp_status=mcp_status
        )
    
    # Validate the output
    #validation_result = company_validator.validate(agent_result["data"])
    
    return CompanyResearchResponse(
        #success=validation_result["valid"],
        success= agent_result["success"],
        data= agent_result["data"], #validation_result["data"] if validation_result["valid"] else
        #validation=validation_result,
        #mcp_status=mcp_status,
        #error=validation_result["error"] if not validation_result["valid"] else None
    )
        


@router.get("/schema")
async def get_company_schema():
    """Get the JSON schema for company research output"""
    return company_validator.get_schema()