from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# Base Models
class Company(BaseModel):
    name: str
    industry: str
    description: str
    products: List[str]
    headquarters: str
    sources: List[str]


class IndustryOpportunity(BaseModel):
    domain: str
    score: float
    rationale: str
    sources: List[str]


class CompetitiveLandscape(BaseModel):
    competitor: str
    product: str
    market_share: float
    note: str
    sources: List[str]


class MarketData(BaseModel):
    market_size_usd: float
    CAGR: float
    key_drivers: List[str]
    sources: List[str]


class MarketGap(BaseModel):
    gap: str
    impact: str
    evidence: str
    source: List[str]


class Opportunity(BaseModel):
    title: str
    priority: str  
    description: str
    sources: List[str]


# Request Models
class MarketDataRequest(BaseModel):
    domain: str


class MarketGapAnalysisRequest(BaseModel):
    company_profile: Company
    competitor_list: List[CompetitiveLandscape]
    market_stats: MarketData


class CompanyResearchRequest(BaseModel):
    company_name: str


class ReportSynthesisRequest(BaseModel):
    """
    PLACEHOLDER: Input schema for Report Synthesis Agent
    
    TODO: Refine schema based on actual agent outputs in issue #47
    """
    company_profile: Optional[Dict[str, Any]] = None
    industry_analysis: Optional[List[Dict[str, Any]]] = None
    market_data: Optional[Dict[str, Any]] = None
    competitive_landscape: Optional[List[Dict[str, Any]]] = None
    market_gaps: Optional[List[Dict[str, Any]]] = None
    opportunities: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_profile": {"name": "Example Corp", "industry": "Technology"},
                "industry_analysis": [{"domain": "AI/ML", "score": 0.9}],
                "market_data": {"market_size_usd": 1000000000},
                "competitive_landscape": [{"competitor": "Competitor A"}],
                "market_gaps": [{"gap": "Missing feature X"}],
                "opportunities": [{"title": "Expand to new market"}]
            }
        }


# Response Models
class BaseResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    raw_response: Optional[str] = None


class CompanyResponse(BaseResponse):
    data: Optional[Company] = None


class IndustryAnalysisResponse(BaseResponse):
    data: Optional[List[IndustryOpportunity]] = None


class CompetitiveLandscapeResponse(BaseResponse):
    data: Optional[List[CompetitiveLandscape]] = None


class MarketDataResponse(BaseResponse):
    data: Optional[MarketData] = None


class MarketGapAnalysisResponse(BaseResponse):
    data: Optional[List[MarketGap]] = None


class OpportunityResponse(BaseResponse):
    data: Optional[List[Opportunity]] = None


class ReportSynthesisResponse(BaseModel):
    """Response model for Report Synthesis Agent"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None
