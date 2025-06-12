from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from src.agents.opportunity_agent import run_opportunity_agent
from src.utils.validation import OpportunityAgentValidator

router = APIRouter()
validator = OpportunityAgentValidator()

# Response model
class OpportunityAgentResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None

@router.post("/", response_model=OpportunityAgentResponse)
async def opportunity_agent_endpoint(request: List[Dict[str, Any]]) -> OpportunityAgentResponse:
    """
    Generate and rank growth opportunities based on market gaps.
    
    Args:
        request: List of market gaps (output of market gap analysis)

    Returns:
        Response with list of growth opportunities or error
    """
    # Validate input
    input_validation = validator.validate_input(request)
    if not input_validation["valid"]:
        return OpportunityAgentResponse(
            success=False,
            error=input_validation["error"]
        )
    
    # Run the agent
    result = run_opportunity_agent(input_validation["data"])
    if not result["success"]:
        return OpportunityAgentResponse(
            success=False,
            error=result["error"],
            raw_response=result.get("raw_response")
        )

    # Validate output
    output_validation = validator.validate_output(result["data"])
    if not output_validation["valid"]:
        return OpportunityAgentResponse(
            success=False,
            error=output_validation["error"],
            raw_response=result.get("raw_response")
        )

    return OpportunityAgentResponse(
        success=True,
        data=output_validation["data"],
        raw_response=result.get("raw_response")
    )

@router.get("/schema/input")
async def get_opportunity_input_schema() -> Dict[str, Any]:
    """Get the input schema for Opportunity Agent"""
    return validator.get_input_schema()

@router.get("/schema/output")
async def get_opportunity_output_schema() -> Dict[str, Any]:
    """Get the output schema for Opportunity Agent"""
    return validator.get_output_schema()
