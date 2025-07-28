import logging
from datetime import datetime

from src.agents.company_research_agent import run_company_research_agent
from src.agents.industry_analysis_agent import run_industry_analysis_agent
from src.agents.market_data_agent import run_market_data_agent
from src.agents.competitive_landscape_agent import run_competitive_landscape_agent
from src.agents.market_gap_agent import run_market_gap_analysis_agent
from src.agents.opportunity_agent import run_opportunity_agent
from src.agents.report_synthesis_agent import run_report_synthesis_agent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def safe_run(agent_fn, input_data, step_name):
    """Executes agent function and returns output in a standard format."""
    try:
        logger.info(f"Running step: {step_name}")
        raw_output = agent_fn(input_data)
        logger.info(f"Step '{step_name}' completed. Output keys: {list(raw_output.keys())}")

        # Normalize output
        if "result" in raw_output:
            return {"result": raw_output["result"]}
        elif "data" in raw_output:
            return {"result": raw_output["data"]}
        elif "raw_response" in raw_output:
            return {"result": raw_output["raw_response"]}
        else:
            return {"result": raw_output}

    except Exception as e:
        logger.error(f"Step '{step_name}' failed: {e}", exc_info=True)
        return {"result": None}


def run_linear_pipeline(company_name: str, selected_domain: str = None) -> dict:
    logger.info(f"Starting pipeline for company: {company_name}")

    # 1. Company Research Agent
    cra_output = safe_run(run_company_research_agent, {"company": company_name}, "CompanyResearch")
    if cra_output["result"] is None:
        return {"success": False, "error": "Company research failed."}
    company_profile = cra_output["result"]

    # 2. Industry Analysis Agent
    ida_output = safe_run(run_industry_analysis_agent, company_profile, "IndustryAnalysis")
    if ida_output["result"] is None:
        return {"success": False, "error": "Industry analysis failed."}
    domains = ida_output["result"].get("domains", [])
    if not domains:
        return {"success": False, "error": "No domains found."}
    domain = selected_domain or domains[0]
    logger.info(f"Selected domain: {domain}")

    # 3. Market Data Agent
    mda_output = safe_run(run_market_data_agent, {"domain": domain}, "MarketData")
    if mda_output["result"] is None:
        return {"success": False, "error": "Market data collection failed."}
    market_data = mda_output["result"]

    # 4. Competitive Landscape Agent
    cla_output = safe_run(run_competitive_landscape_agent, {"domain": domain}, "CompetitiveLandscape")
    if cla_output["result"] is None:
        return {"success": False, "error": "Competitive landscape analysis failed."}
    competitive_data = cla_output["result"]

    # 5. Gap Analysis Agent
    ga_input = {
        "market_data": market_data,
        "competitive_landscape": competitive_data
    }
    ga_output = safe_run(run_market_gap_analysis_agent, ga_input, "GapAnalysis")
    if ga_output["result"] is None:
        return {"success": False, "error": "Gap analysis failed."}
    market_gaps = ga_output["result"]

    # 6. Opportunity Agent
    oa_output = safe_run(run_opportunity_agent, market_gaps, "OpportunityAnalysis")
    if oa_output["result"] is None:
        return {"success": False, "error": "Opportunity analysis failed."}
    opportunities = oa_output["result"]



    # 7. Report Synthesis Agent
    report_input = {
        "company_research_data": company_profile,
        "domain_research_data": ida_output['result'],
        "market_research_data": market_data,
        "competitive_research_data": competitive_data,
        "gap_analysis_data": market_gaps,
        "opportunity_research_data": opportunities
    }

    try:
        report_output = run_report_synthesis_agent(report_input)
        final_data = report_output.get("data", report_output)  # fallback in case it's directly returned

        return {
            "success": True,
            "pdf_content": final_data["pdf_content"],
            "report_title": final_data["report_title"],
            "generated_at": final_data["generated_at"],
            "placeholder": final_data.get("placeholder", True)
        }
    except Exception as e:
        logger.error("Report Synthesis Agent failed.", exc_info=True)
        return {
            "success": False,
            "error": "Report synthesis failed.",
            "details": str(e)
        }
