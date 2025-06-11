from fastapi import APIRouter
from .company_research_routes import router as company_research_router
from .industry_analysis_routes import router as industry_analysis_router
from .competitive_landscape_routes import router as competitive_landscape_router
from .market_data_routes import router as market_data_router
from .opportunity_routes import router as opportunity_router

# Main router that combines all sub-routers
api_router = APIRouter()

# Include all route modules
api_router.include_router(company_research_router, prefix="/company-research", tags=["company_research"])
api_router.include_router(industry_analysis_router, prefix="/industry-analysis", tags=["industry_analysis"])
api_router.include_router(competitive_landscape_router, prefix="/competitive-landscape", tags=["competitive_landscape"])
api_router.include_router(market_data_router, prefix="/market-data", tags=["market_data"])
api_router.include_router(opportunity_router, prefix="/opportunity", tags=["opportunity"])
