from fastapi import APIRouter
from company_research_routes import router as company_research_router

# Main router that combines all sub-routers
api_router = APIRouter()

# Include all route modules
api_router.include_router(company_research_router, prefix="/company_research", tags=["company_research"])

# Future agent routes can be added here:
# api_router.include_router(market_router, prefix="/market", tags=["market"])
# api_router.include_router(financial_router, prefix="/financial", tags=["financial"])
