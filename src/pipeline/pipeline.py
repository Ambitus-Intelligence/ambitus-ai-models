import logging
import json
from datetime import datetime
from pydantic import ValidationError
from typing import List, Any

# Import Pydantic models
from src.utils.models import (
    CompanyResponse,
    IndustryAnalysisResponse,
    MarketDataResponse,
    CompanyResearchRequest,
    CompetitiveLandscapeResponse,
    MarketGapAnalysisResponse,
    OpportunityResponse,
    ReportSynthesisResponse,
    MarketDataRequest,
    MarketGapAnalysisRequest,
    ReportSynthesisRequest,
)

# Import agent runners
from src.agents.company_research_agent import run_company_research_agent
from src.agents.industry_analysis_agent import run_industry_analysis_agent
from src.agents.market_data_agent import run_market_data_agent
from src.agents.competitive_landscape_agent import run_competitive_landscape_agent
from src.agents.market_gap_agent import run_market_gap_analysis_agent
from src.agents.opportunity_agent import run_opportunity_agent
from src.agents.report_synthesis_agent import run_report_synthesis_agent

# Logging setup
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


def _pretty(obj: Any) -> str:
    """Safely JSON stringify for logging"""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return str(obj)


def safe_run(agent_fn, input_data, response_model, step_name: str):
    """Executes agent, validates with Pydantic response model, and returns `.data`"""
    try:
        logger.info("=== [%s] BEGIN ===", step_name)
        logger.debug("[%s] INPUT:\n%s", step_name, _pretty(
            input_data.model_dump() if hasattr(input_data, "model_dump") else input_data
        ))
        raw_output = agent_fn(input_data)
        logger.debug("[%s] RAW OUTPUT:\n%s", step_name, _pretty(raw_output))
    except Exception:
        logger.exception("[%s] Agent raised exception", step_name)
        return None

    try:
        if isinstance(raw_output, response_model):
            validated = raw_output
        else:
            validated = response_model(**(raw_output or {}))
        logger.debug("[%s] VALIDATED:\n%s", step_name, _pretty(validated.model_dump()))
    except ValidationError as ve:
        logger.error("[%s] ValidationError:\n%s", step_name, ve)
        return None
    except Exception:
        logger.exception("[%s] Unexpected validation error", step_name)
        return None

    if not validated.success or validated.data is None:
        logger.error("[%s] FAILED | Reason: %s", step_name, getattr(validated, "error", "Unknown"))
        return None

    logger.info("=== [%s] END (ok) ===", step_name)
    return validated.data


def select_domain_from_user(domains: List[str]) -> str:
    """Prompt user to select a domain"""
    print("\nAvailable domains:")
    for idx, d in enumerate(domains, 1):
        print(f"{idx}. {d}")
    choice = input("Enter number or name (default=1): ").strip()

    if not choice:
        return domains[0]
    if choice.isdigit() and 1 <= int(choice) <= len(domains):
        return domains[int(choice) - 1]
    return next((d for d in domains if d.lower() == choice.lower()), domains[0])


def run_pipeline(company_name: str) -> ReportSynthesisResponse:
    logger.info(f"=== PIPELINE START for {company_name} ===")

    # 1. Company Research
    company_data = safe_run(
        run_company_research_agent,
        CompanyResearchRequest(company_name=company_name),
        CompanyResponse,
        "CompanyResearch"
    )
    if not company_data:
        return ReportSynthesisResponse(success=False, error="Company research failed.")

    # 2. Industry Analysis
    industry_data = safe_run(
        run_industry_analysis_agent,
        company_data,
        IndustryAnalysisResponse,
        "IndustryAnalysis"
    )
    if not industry_data:
        return ReportSynthesisResponse(success=False, error="Industry analysis failed.")

    # 3. Domain selection
    domain = select_domain_from_user([op.domain for op in industry_data])
    logger.info(f"Domain selected: {domain}")

    # 4. Market Data
    market_data = safe_run(
        run_market_data_agent,
        MarketDataRequest(domain=domain),
        MarketDataResponse,
        "MarketData"
    )
    if not market_data:
        return ReportSynthesisResponse(success=False, error="Market data failed.")

    # 5. Competitive Landscape
    competitive_data = safe_run(
        run_competitive_landscape_agent,
        {"domain": domain},  # 🔹 fix if your agent expects request model
        CompetitiveLandscapeResponse,
        "CompetitiveLandscape"
    )
    if not competitive_data:
        return ReportSynthesisResponse(success=False, error="Competitive landscape failed.")

    # 6. Market Gap Analysis
    gap_analysis = safe_run(
        run_market_gap_analysis_agent,
        MarketGapAnalysisRequest(
            company_profile=company_data,
            competitor_list=competitive_data,
            market_stats=market_data
        ),
        MarketGapAnalysisResponse,
        "GapAnalysis"
    )
    if not gap_analysis:
        return ReportSynthesisResponse(success=False, error="Gap analysis failed.")

    # 7. Opportunity Analysis
    opportunities = safe_run(
        run_opportunity_agent,
        gap_analysis,
        OpportunityResponse,
        "OpportunityAnalysis"
    )
    if not opportunities:
        return ReportSynthesisResponse(success=False, error="Opportunity analysis failed.")

    # 8. Report Synthesis
    report_resp = run_report_synthesis_agent(
        ReportSynthesisRequest(
            company_research_data=company_data,
            domain_research_data=industry_data,
            market_research_data=market_data,
            competitive_research_data=competitive_data,
            gap_analysis_data=gap_analysis,
            opportunity_research_data=opportunities,
        )
    )

    # Ensure correct response type
    try:
        if isinstance(report_resp, ReportSynthesisResponse):
            return report_resp
        return ReportSynthesisResponse(**(report_resp or {}))
    except ValidationError as ve:
        logger.error("ReportSynthesis validation error: %s", ve)
        return ReportSynthesisResponse(success=False, error="Report synthesis validation failed.")


if __name__ == "__main__":
    result = run_pipeline("OpenAI")
    print("\n=== PIPELINE RESULT ===")
    print(result.model_dump())
    
# This code is part of a pipeline that runs a series of agents to gather and synthesize information about a company.
# It includes error handling, logging, and user interaction for domain selection.
# The pipeline is designed to be modular and extensible for future agents or steps.