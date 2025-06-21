from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from src.agents.market_data_agent import run_market_data_agent
from src.utils.validation import MarketDataValidator

router = APIRouter()
market_data_validator = MarketDataValidator()

# Request schema
class MarketDataRequest(BaseModel):
    domain: str

# Response schema
class MarketDataResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None

@router.post("/", response_model=MarketDataResponse, tags=["market_data"])
async def fetch_market_data(request: MarketDataRequest) -> MarketDataResponse:
    """
    Fetch market data for a given domain using the Market Data Agent.
    """
    try:
        agent_result = run_market_data_agent(request.domain)

        if not agent_result["success"]:
            return MarketDataResponse(
                success=False,
                error=agent_result["error"],
                raw_response=agent_result.get("raw_response")
            )

        validation_result = market_data_validator.validate_output(agent_result["data"])

        if not validation_result["valid"]:
            return MarketDataResponse(
                success=False,
                error=validation_result["error"],
                raw_response=agent_result.get("raw_response")
            )

        return MarketDataResponse(
            success=True,
            data=validation_result["data"],
            raw_response=agent_result.get("raw_response")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/input", tags=["market_data"])
async def get_market_data_input_schema() -> Dict[str, Any]:
    """Return input schema for Market Data Agent"""
    return {
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Domain or industry to fetch market data for"
            }
        },
        "required": ["domain"]
    }


@router.get("/schema/output", tags=["market_data"])
async def get_market_data_output_schema() -> Dict[str, Any]:
    """Return output schema for Market Data Agent"""
    return market_data_validator.get_output_schema()
