from fastapi import APIRouter
from typing import Dict, Any, List
import json

from src.agents.opportunity_agent import run_opportunity_agent
from src.utils.validation import OpportunityValidator
from src.utils.models import MarketGap, OpportunityResponse

router = APIRouter()
validator = OpportunityValidator()

# -------------------- POST ENDPOINT --------------------

@router.post("/", response_model=OpportunityResponse)
async def opportunity_agent_endpoint(request: List[MarketGap]) -> OpportunityResponse:
    """
    Generate and rank growth opportunities based on market gaps.

    Args:
        request: List of validated MarketGap objects

    Returns:
        Structured opportunity list or error details
    """
    input_list = [item.model_dump() for item in request]

    # Validate input
    input_validation = validator.validate_input(input_list)
    if not input_validation["valid"]:
        return OpportunityResponse(
            success=False,
            error=input_validation["error"]
        )

    try:
        # Run the agent
        result = run_opportunity_agent(input_validation["data"])

        # Ensure result is a dict with success flag and data list
        if not isinstance(result, dict) or not result.get("success") or not isinstance(result.get("data"), list):
            return OpportunityResponse(
                success=False,
                error="Agent returned an unexpected response format (expected a dict with a list under 'data').",
                raw_response=json.dumps(result)
            )

        # Validate output
        output_validation = validator.validate_output(result["data"])
        if not output_validation["valid"]:
            return OpportunityResponse(
                success=False,
                error=output_validation["error"],
                raw_response=result.get("raw_response")
            )

        return OpportunityResponse(
            success=True,
            data=output_validation["data"],
            raw_response=result.get("raw_response")
        )

    except Exception as e:
        return OpportunityResponse(
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
