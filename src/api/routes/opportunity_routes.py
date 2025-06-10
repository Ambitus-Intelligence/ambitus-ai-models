from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from src.agents.opportunity_agent import run_opportunity_agent
from src.utils.validation import OpportunityAgentValidator

# FastAPI router
router = APIRouter()
opportunity_validator = OpportunityAgentValidator()

# Input schema
class OpportunityAgentRequest(BaseModel):
    market_gaps: List[str]

# Output schema
class Opportunity(BaseModel):
    title: str
    priority: str
    description: str
    sources: List[str]

# POST endpoint
@router.post("/", response_model=List[Opportunity])
async def opportunity_agent_endpoint(request_data: OpportunityAgentRequest):
    """
    Generate and rank growth opportunities based on market gaps.
    Returns a list of opportunity objects.
    """
    try:
        result = run_opportunity_agent(request_data.dict())

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])

        validation = opportunity_validator.validate_output(result["data"])

        if not validation["valid"]:
            raise HTTPException(status_code=422, detail=validation["error"])

        return validation["data"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Input schema endpoint
@router.get("/schema/input")
async def get_opportunity_input_schema() -> Dict[str, Any]:
    """Return input schema for Opportunity Agent"""
    return {
        "type": "object",
        "properties": {
            "market_gaps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of identified market gaps"
            }
        },
        "required": ["market_gaps"]
    }

# Output schema endpoint
@router.get("/schema/output")
async def get_opportunity_output_schema() -> Dict[str, Any]:
    """Return output schema for Opportunity Agent"""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {"type": "string"},
                "description": {"type": "string"},
                "sources": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["title", "priority", "description", "sources"]
        }
    }
