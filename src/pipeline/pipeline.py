from haystack import Pipeline
from agents.company_research_agent import CompanyResearchAgent
from agents.industry_analysis_agent import IndustryAnalysisAgent
from agents.market_data_agent import MarketDataAgent
from agents.competitive_landscape_agent import CompetitiveLandscapeAgent
from agents.market_gap_agent import GapAnalysisAgent
from agents.opportunity_agent import OpportunityAgent
from agents.report_synthesis_agent import ReportSynthesisAgent
# from agents.citation_agent import CitationAgent


def build_branching_pipeline() -> Pipeline:
    pipeline = Pipeline()

    # Instantiate agents
    cra = CompanyResearchAgent()
    ida = IndustryAnalysisAgent()
    mda = MarketDataAgent()
    cla = CompetitiveLandscapeAgent()
    ga = GapAnalysisAgent()
    oa = OpportunityAgent()
    rsa = ReportSynthesisAgent()
    # cit = CitationAgent()  # Optional tool

    # Add nodes
    pipeline.add_node(component=cra, name="CompanyResearch", inputs=["Query"])
    pipeline.add_node(component=ida, name="IndustryAnalysis", inputs=[])
    
    # Domain Selection: emulate branching (no built-in router or decision node (yet))
    pipeline.add_node(component=mda, name="MarketData", inputs=[])
    pipeline.add_node(component=cla, name="CompetitiveLandscape", inputs=[])

    pipeline.add_node(component=ga, name="GapAnalysis", inputs=[])
    pipeline.add_node(component=oa, name="OpportunityAnalysis", inputs=[])
    pipeline.add_node(component=rsa, name="ReportSynthesis", inputs=[])
    # pipeline.add_node(component=cit, name="Citation", inputs=[])

    # Connect main flow
    pipeline.connect("CompanyResearch", "IndustryAnalysis")

    # "Domain Selection" → branch to MarketData and CompetitiveLandscape in parallel
    pipeline.connect("IndustryAnalysis", "MarketData")
    pipeline.connect("IndustryAnalysis", "CompetitiveLandscape")

    # Merge outputs into GapAnalysis
    pipeline.connect("MarketData", "GapAnalysis.input_1")
    pipeline.connect("CompetitiveLandscape", "GapAnalysis.input_2")

    # Continue downstream
    pipeline.connect("GapAnalysis", "OpportunityAnalysis")
    pipeline.connect("OpportunityAnalysis", "ReportSynthesis")

    return pipeline
