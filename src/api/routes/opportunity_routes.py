from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from src.agents.opportunity_agent import run_opportunity_agent
from src.utils.validation import OpportunityAgentValidator
import json

router = APIRouter()
validator = OpportunityAgentValidator()

# -------------------- MODELS --------------------

class MarketGapItem(BaseModel):
    gap: str
    impact: str
    evidence: str
    source: List[str]

class OpportunityAgentResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None

# -------------------- POST ENDPOINT --------------------

@router.post("/", response_model=OpportunityAgentResponse)
async def opportunity_agent_endpoint(request: List[MarketGapItem]) -> OpportunityAgentResponse:
    """
    Generate and rank growth opportunities based on market gaps.

    Args:
        request: List of market gap dictionaries

    Returns:
        Structured opportunity list or error details
    """
    input_list = [item.model_dump() for item in request]

    # Validate input
    input_validation = validator.validate_input(input_list)
    if not input_validation["valid"]:
        return OpportunityAgentResponse(
            success=False,
            error=input_validation["error"]
        )

    try:
        # Run the agent
        result = run_opportunity_agent(input_validation["data"])

        # Ensure result is a dict with success flag and data list
        if not isinstance(result, dict) or not result.get("success") or not isinstance(result.get("data"), list):
            return OpportunityAgentResponse(
                success=False,
                error="Agent returned an unexpected response format (expected a dict with a list under 'data').",
                raw_response=json.dumps(result)
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

    except Exception as e:
        return OpportunityAgentResponse(
            success=False,
            error=f"Unhandled exception in agent execution: {str(e)}"
        )

# -------------------- SCHEMA ENDPOINTS --------------------

@router.get("/schema/input")
async def get_opportunity_input_schema() -> Dict[str, Any]:
    return validator.get_input_schema()

@router.get("/schema/output")
async def get_opportunity_output_schema() -> Dict[str, Any]:
    return validator.get_output_schema()
