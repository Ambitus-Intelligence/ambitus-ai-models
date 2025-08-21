from typing import Dict, Any, Optional
from rich.prompt import Prompt, Confirm
from rich.console import Console
from rich.table import Table

from src.agents.company_research_agent import run_company_research_agent
from src.agents.industry_analysis_agent import run_industry_analysis_agent
from src.agents.market_data_agent import run_market_data_agent
from src.agents.competitive_landscape_agent import run_competitive_landscape_agent
from src.agents.market_gap_agent import run_market_gap_analysis_agent
from src.agents.opportunity_agent import run_opportunity_agent
from src.agents.report_synthesis_agent import run_report_synthesis_agent


class AgentExecutor:
    """Handles agent execution and data flow"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def execute_agent(self, agent_name: str, agent_input: Dict, selected_domain: str = None) -> Dict:
        """Execute actual agent based on agent type"""
        try:
            if agent_name == "Company Research Agent":
                company_name = agent_input.get("company_name", "")
                response = run_company_research_agent(company_name)
                
            elif agent_name == "Industry Analysis Agent":
                company_data = agent_input.get("company_data")
                if not company_data:
                    raise ValueError("Company data required from previous agent")
                response = run_industry_analysis_agent(company_data)
                
            elif agent_name == "Market Data Agent":
                domain = selected_domain or agent_input.get("domain", "")
                if not domain:
                    raise ValueError("Domain required for market data analysis")
                response = run_market_data_agent(domain)
                
            elif agent_name == "Competitive Landscape Agent":
                if not selected_domain:
                    raise ValueError("Domain selection required from previous agent")
                
                industry_opportunity = {
                    "domain": selected_domain,
                    "score": 0.8,
                    "rationale": f"Selected domain: {selected_domain}",
                    "sources": []
                }
                response = run_competitive_landscape_agent(industry_opportunity)
                
            elif agent_name == "Market Gap Analysis Agent":
                combined_data = agent_input.get("combined_data")
                if not combined_data:
                    raise ValueError("Combined data required from previous agents")
                response = run_market_gap_analysis_agent(combined_data)
                
            elif agent_name == "Opportunity Agent":
                gap_analysis = agent_input.get("gap_analysis")
                if not gap_analysis:
                    raise ValueError("Gap analysis data required from previous agent")
                response = run_opportunity_agent(gap_analysis)
                
            elif agent_name == "Report Synthesis Agent":
                combined_data = agent_input.get("combined_data")
                if not combined_data:
                    raise ValueError("Combined data required from all previous agents")
                response = run_report_synthesis_agent(combined_data)
            
            else:
                raise ValueError(f"Unknown agent: {agent_name}")
            
            return response
                
        except Exception as e:
            return {
                "agent_name": agent_name,
                "execution_status": "failed",
                "success": False,
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
    
    def collect_agent_input(self, agent_name: str, agent_outputs: Dict, selected_domain: str = None) -> Optional[Dict]:
        """Collect input for the agent based on actual requirements"""
        if agent_name == "Company Research Agent":
            company_name = Prompt.ask("Enter company name", default="")
            return {"company_name": company_name} if company_name else None
                
        elif agent_name == "Industry Analysis Agent":
            company_data = self._get_data_from_agent("Company Research Agent", agent_outputs)
            return {"company_data": company_data} if company_data else None
                
        elif agent_name == "Market Data Agent":
            if selected_domain:
                use_selected = Confirm.ask(f"Use selected domain '{selected_domain}'?", default=True)
                if use_selected:
                    return {"domain": selected_domain}
            
            domain = Prompt.ask("Enter market domain to analyze", default="")
            return {"domain": domain} if domain else None
                
        elif agent_name == "Competitive Landscape Agent":
            if selected_domain:
                self.console.print(f"[green]Using selected domain: {selected_domain}[/green]")
                return {"auto_chain": True}
            return None
                
        elif agent_name == "Market Gap Analysis Agent":
            company_profile = self._get_data_from_agent("Company Research Agent", agent_outputs)
            competitor_list = self._get_data_from_agent("Competitive Landscape Agent", agent_outputs)
            market_stats = self._get_data_from_agent("Market Data Agent", agent_outputs)
            
            if all([company_profile, competitor_list, market_stats]):
                combined_data = {
                    "company_profile": company_profile,
                    "competitor_list": competitor_list,
                    "market_stats": market_stats
                }
                return {"combined_data": combined_data}
            return None
                
        elif agent_name == "Opportunity Agent":
            gap_analysis = self._get_data_from_agent("Market Gap Analysis Agent", agent_outputs)
            return {"gap_analysis": gap_analysis} if gap_analysis else None
                
        elif agent_name == "Report Synthesis Agent":
            combined_data = {
                "company_research_data": self._get_data_from_agent("Company Research Agent", agent_outputs),
                "domain_research_data": self._get_data_from_agent("Industry Analysis Agent", agent_outputs),
                "market_research_data": self._get_data_from_agent("Market Data Agent", agent_outputs),
                "competitive_research_data": self._get_data_from_agent("Competitive Landscape Agent", agent_outputs),
                "gap_analysis_data": self._get_data_from_agent("Market Gap Analysis Agent", agent_outputs),
                "opportunity_research_data": self._get_data_from_agent("Opportunity Agent", agent_outputs)
            }
            return {"combined_data": combined_data}
        
        return {"auto_chain": True}
    
    def _get_data_from_agent(self, agent_name: str, agent_outputs: Dict) -> Optional[Dict]:
        """Get data from a specific agent output"""
        output = agent_outputs.get(agent_name)
        if output and output.get("success") and output.get("data"):
            return output["data"]
        return None
    
    def handle_domain_selection(self, industry_opportunities: list) -> Optional[str]:
        """Handle domain selection after industry analysis"""
        if not industry_opportunities:
            return None
        
        self.console.print("\n[bold]Industry Opportunities Found:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Index", style="dim", width=6)
        table.add_column("Domain", min_width=20)
        table.add_column("Score", justify="right", width=10)
        table.add_column("Rationale", min_width=40)
        
        for i, opp in enumerate(industry_opportunities):
            table.add_row(
                str(i + 1),
                opp.get("domain", "Unknown"),
                f"{opp.get('score', 0):.2f}",
                opp.get("rationale", "No rationale provided")[:50] + "..."
            )
        
        self.console.print(table)
        
        # Get user selection
        while True:
            try:
                selection = Prompt.ask(
                    f"Select domain for further analysis (1-{len(industry_opportunities)})",
                    default="1"
                )
                index = int(selection) - 1
                if 0 <= index < len(industry_opportunities):
                    selected_domain = industry_opportunities[index].get("domain")
                    self.console.print(f"[green]Selected domain: {selected_domain}[/green]")
                    return selected_domain
                else:
                    self.console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")
