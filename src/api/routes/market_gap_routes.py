from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.agents.market_gap_agent import run_market_gap_analysis_agent
from src.utils.validation import MarketGapAnalysisValidator
from src.utils.models import MarketGapAnalysisRequest, MarketGapAnalysisResponse

router = APIRouter()

# Initialize validator
validator = MarketGapAnalysisValidator()

@router.post("/", response_model=MarketGapAnalysisResponse)
async def analyze_market_gaps(request: MarketGapAnalysisRequest) -> MarketGapAnalysisResponse:
    """
    Analyze a company profile, competitor list and market stats to give market gaps.
    
    Args:
        Request: Company profile, Competitor list, Market stats
        
    Returns:
        Response containing success status and market gap analysis data or error
    """
    # Convert request to dict for validation
    incoming_data_dict = request.model_dump()
    
    # Validate input
    input_validation = validator.validate_input(incoming_data_dict)
    if not input_validation["valid"]:
        return MarketGapAnalysisResponse(
            success=False,
            error=f"Invalid input data: {input_validation['error']}"
        )
    
    # Run the market gap analyst agent
    result = run_market_gap_analysis_agent(input_validation["data"])
    
    if not result["success"]:
        return MarketGapAnalysisResponse(
            success=False,
            error=result['error'],
            raw_response=result.get("raw_response")
        )
    
    # Validate output
    output_validation = validator.validate_output(result["data"])
    if not output_validation["valid"]:
        return MarketGapAnalysisResponse(
            success=False,
            error=output_validation['error'],
            raw_response=result.get("raw_response")
        )
    
    return MarketGapAnalysisResponse(
        success=True,
        data=output_validation["data"],
        raw_response=result.get("raw_response")
    )

@router.get("/schema/input")
async def get_input_schema() -> Dict[str, Any]:
    """Get the input schema for industry analysis"""
    return validator.get_input_schema()

@router.get("/schema/output")
async def get_output_schema() -> Dict[str, Any]:
    """Get the output schema for industry analysis"""
    return validator.get_output_schema()