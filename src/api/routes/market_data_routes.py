from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from src.agents.market_data_agent import run_market_data_agent  

router = APIRouter()

class MarketDataRequest(BaseModel):
    domain: str

@router.post("/fetch", tags=["market_data"])
async def fetch_market_data(request: MarketDataRequest) -> Dict[str, Any]:
    try:
        result = run_market_data_agent(request.domain)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
