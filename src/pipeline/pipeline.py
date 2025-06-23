from haystack import Pipeline
from agents.company_research_agent import CompanyResearchAgent
from agents.industry_analysis_agent import IndustryAnalysisAgent
from agents.market_data_agent import MarketDataAgent
from agents.competitive_landscape_agent import CompetitiveLandscapeAgent
from agents.market_gap_agent import GapAnalysisAgent
from agents.opportunity_agent import OpportunityAgent
from agents.report_synthesis_agent import ReportSynthesisAgent
# from agents.citation_agent import CitationAgent


def run_linear_pipeline(company_name: str, selected_domain: str = None) -> str:
    """
    Executes the linear pipeline and returns path to the final PDF.
    """
    # citation_agent = CitationAgent()
    # all_citations = []

    # 1. Company Research
    cra = CompanyResearchAgent()
    cra_output = cra.run({"company": company_name})
    # all_citations.extend(citation_agent.run(step="CompanyResearch", content=cra_output["citations"]))

    # 2. Industry Analysis
    ida = IndustryAnalysisAgent()
    ida_output = ida.run(cra_output["result"])
    # all_citations.extend(citation_agent.run(step="IndustryAnalysis", content=ida_output["citations"]))

    # 3. Domain Selection (simple pick for now)
    domain = selected_domain or ida_output["result"]["domains"][0]

    # 4. Market Data (for selected domain)
    mda = MarketDataAgent()
    mda_output = mda.run({"domain": domain})
    # all_citations.extend(citation_agent.run(step="MarketData", content=mda_output["citations"]))

    # 5. Competitive Landscape
    cla = CompetitiveLandscapeAgent()
    cla_output = cla.run(mda_output["result"])
    # all_citations.extend(citation_agent.run(step="CompetitiveLandscape", content=cla_output["citations"]))

    # 6. Gap Analysis
    ga = GapAnalysisAgent()
    ga_output = ga.run(cla_output["result"])
    # all_citations.extend(citation_agent.run(step="GapAnalysis", content=ga_output["citations"]))

    # 7. Opportunity Agent
    oa = OpportunityAgent()
    oa_output = oa.run(ga_output["result"])
    # all_citations.extend(citation_agent.run(step="OpportunityAnalysis", content=oa_output["citations"]))

    # 8. Report Synthesis + PDF generation
    rsa = ReportSynthesisAgent()
    report_path = rsa.run({
        "opportunities": oa_output["result"],
        # "citations": all_citations,
        "format": "pdf",
        "company": company_name
    })["pdf_path"]

    return report_path
