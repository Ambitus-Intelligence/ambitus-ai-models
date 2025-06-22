from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from src.agents.industry_analysis_agent import run_industry_analysis_agent
from src.utils.validation import IndustryAnalysisValidator
from src.utils.models import Company, IndustryAnalysisResponse

router = APIRouter()

# Initialize validator
validator = IndustryAnalysisValidator()

@router.post("/", response_model=IndustryAnalysisResponse)
async def analyze_industry_opportunities(request: Company) -> IndustryAnalysisResponse:
    """
    Analyze a company profile and return ranked industry expansion opportunities.
    
    Args:
        request: Company profile data
        
    Returns:
        Response containing success status and industry opportunities or error
    """
    # Convert request to dict for validation
    company_data = request.model_dump()
    
    # Validate input
    input_validation = validator.validate_input(company_data)
    if not input_validation["valid"]:
        return IndustryAnalysisResponse(
            success=False,
            error=f"Invalid input data: {input_validation['error']}"
        )
    
    # Run the industry analysis agent
    result = run_industry_analysis_agent(input_validation["data"])
    
    if not result["success"]:
        return IndustryAnalysisResponse(
            success=False,
            error=result['error'],
            raw_response=result.get("raw_response")
        )
    
    # Validate output
    output_validation = validator.validate_output(result["data"])
    if not output_validation["valid"]:
        return IndustryAnalysisResponse(
            success=False,
            error=output_validation['error'],
            raw_response=result.get("raw_response")
        )
    
    return IndustryAnalysisResponse(
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