from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.agents.market_data_agent import run_market_data_agent
from src.utils.validation import MarketDataValidator
from src.utils.models import MarketDataRequest, MarketDataResponse


router = APIRouter()
validator = MarketDataValidator()

@router.post("/", response_model=MarketDataResponse, tags=["market_data"])
async def fetch_market_data(request: MarketDataRequest) -> MarketDataResponse:
    """
    Fetch market data for a given domain using the Market Data Agent.
    """
    try:
        # Validate input
        input_validation = validator.validate_input(request.model_dump())
        if not input_validation["valid"]:
            return MarketDataResponse(success=False, error=input_validation["error"])

        # Run agent
        agent_result = run_market_data_agent(input_validation["data"]["domain"])

        if not agent_result["success"]:
            return MarketDataResponse(
                success=False,
                error=agent_result["error"],
                raw_response=agent_result.get("raw_response")
            )

        # Validate output
        output_validation = validator.validate_output(agent_result["data"])
        if not output_validation["valid"]:
            return MarketDataResponse(
                success=False,
                error=output_validation["error"],
                raw_response=agent_result.get("raw_response")
            )

        return MarketDataResponse(
            success=True,
            data=output_validation["data"],
            raw_response=agent_result.get("raw_response")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/input", tags=["market_data"])
async def get_market_data_input_schema() -> Dict[str, Any]:
    """Return input schema for Market Data Agent."""
    return validator.get_input_schema()


@router.get("/schema/output", tags=["market_data"])
async def get_market_data_output_schema() -> Dict[str, Any]:
    """Return output schema for Market Data Agent."""
    return validator.get_output_schema()
