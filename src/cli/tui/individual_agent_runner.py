import os
import sys
import json
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax

# Import actual models and agents
from src.utils.models import (
    CompanyResearchRequest, MarketDataRequest, MarketGapAnalysisRequest,
    ReportSynthesisRequest, CompanyResponse, IndustryAnalysisResponse,
    MarketDataResponse, CompetitiveLandscapeResponse, MarketGapAnalysisResponse,
    OpportunityResponse, ReportSynthesisResponse
)
from src.agents.company_research_agent import run_company_research_agent
from src.agents.industry_analysis_agent import run_industry_analysis_agent
from src.agents.market_data_agent import run_market_data_agent
from src.agents.competitive_landscape_agent import run_competitive_landscape_agent
from src.agents.market_gap_agent import run_market_gap_analysis_agent
from src.agents.opportunity_agent import run_opportunity_agent
from src.agents.report_synthesis_agent import run_report_synthesis_agent

# Import validators
from src.utils.validation import (
    CompanyValidator, IndustryAnalysisValidator, MarketDataValidator,
    CompetitiveLandscapeValidator, MarketGapAnalysisValidator,
    OpportunityValidator, ReportSynthesisValidator
)

class IndividualAgentRunner:
    """Handles individual agent execution with two-panel layout"""
    
    def __init__(self, console: Console):
        self.console = console
        self.agents = self._get_agent_definitions()
        self.current_agent_index = 0
        self.current_tab = "input"  # input, output, description
        self.agent_outputs = {}  # Store outputs for chaining
        self.selected_domain = None  # Store selected domain from industry analysis
        self.output_scroll_offset = 0  # For output scrolling
        self.output_lines_per_page = 20  # Lines to show per page
        self._initialize_validators()
        
    def _initialize_validators(self):
        """Initialize validators for each agent"""
        self.validators = {
            "Company Research Agent": CompanyValidator(),
            "Industry Analysis Agent": IndustryAnalysisValidator(),
            "Market Data Agent": MarketDataValidator(),
            "Competitive Landscape Agent": CompetitiveLandscapeValidator(),
            "Market Gap Analysis Agent": MarketGapAnalysisValidator(),
            "Opportunity Agent": OpportunityValidator(),
            "Report Synthesis Agent": ReportSynthesisValidator()
        }
    
    def _get_agent_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Define all available agents with their actual specifications"""
        return {
            "Company Research Agent": {
                "description": """
## Company Research Agent

**Purpose:** Collect foundational company data and business intelligence.

**Key Functions:**
- Company background and history research
- Business model analysis
- Financial performance overview
- Leadership and organizational structure
- Current market position assessment

**Input Requirements:**
- Company name (required)

**Output Format:**
- Company profile with name, industry, description
- Product/service listings
- Headquarters location
- Source references
""",
                "input_schema": {
                    "company_name": "str - Company name to research (required)"
                },
                "request_model": CompanyResearchRequest,
                "response_model": CompanyResponse,
                "next_agent": "Industry Analysis Agent"
            },
            "Industry Analysis Agent": {
                "description": """
## Industry Analysis Agent

**Purpose:** Analyze industry trends and identify expansion domains.

**Key Functions:**
- Industry landscape mapping
- Market trend analysis
- Growth opportunity identification
- Domain scoring and rationale

**Input Requirements:**
- Company context from previous agent
- Industry information

**Output Format:**
- List of industry opportunities with scores
- Domain analysis with rationale
- Source references
""",
                "input_schema": {
                    "company_data": "Company - Company profile from Company Research Agent"
                },
                "request_model": CompanyResponse,
                "response_model": IndustryAnalysisResponse,
                "next_agent": "Market Data Agent"
            },
            "Market Data Agent": {
                "description": """
## Market Data Agent

**Purpose:** Fetch quantitative market metrics and data.

**Key Functions:**
- Market size and valuation data
- Growth rate calculations (CAGR)
- Key market drivers identification
- Quantitative market analysis

**Input Requirements:**
- Domain/market to analyze

**Output Format:**
- Market size in USD
- CAGR (Compound Annual Growth Rate)
- Key market drivers
- Source references
""",
                "input_schema": {
                    "domain": "str - Market domain to analyze"
                },
                "request_model": MarketDataRequest,
                "response_model": MarketDataResponse,
                "next_agent": "Competitive Landscape Agent"
            },
            "Competitive Landscape Agent": {
                "description": """
## Competitive Landscape Agent

**Purpose:** Map competitors and their market offerings.

**Key Functions:**
- Competitor identification and profiling
- Market share analysis
- Product/service comparison
- Competitive positioning

**Input Requirements:**
- Industry/domain context
- Company context

**Output Format:**
- List of competitors with profiles
- Market share data
- Product comparisons
- Strategic notes and insights
""",
                "input_schema": {
                    "company_data": "Company - Company context",
                    "domain": "str - Industry domain to analyze"
                },
                "request_model": "InferredFromContext",
                "response_model": CompetitiveLandscapeResponse,
                "next_agent": "Market Gap Analysis Agent"
            },
            "Market Gap Analysis Agent": {
                "description": """
## Market Gap Analysis Agent

**Purpose:** Detect unmet market needs and opportunities.

**Key Functions:**
- Gap identification in current market
- Impact assessment of gaps
- Evidence collection for gaps
- Opportunity validation

**Input Requirements:**
- Company profile
- Competitor landscape
- Market statistics

**Output Format:**
- Identified market gaps
- Impact assessment for each gap
- Supporting evidence
- Source references
""",
                "input_schema": {
                    "company_profile": "Company - Company profile data",
                    "competitor_list": "List[CompetitiveLandscape] - Competitor analysis",
                    "market_stats": "MarketData - Market statistics"
                },
                "request_model": MarketGapAnalysisRequest,
                "response_model": MarketGapAnalysisResponse,
                "next_agent": "Opportunity Agent"
            },
            "Opportunity Agent": {
                "description": """
## Opportunity Agent

**Purpose:** Generate specific growth opportunities and strategies.

**Key Functions:**
- Business opportunity generation
- Priority assessment
- Strategic recommendations
- Implementation guidance

**Input Requirements:**
- Market gap analysis results
- Company context

**Output Format:**
- Prioritized opportunity list
- Detailed descriptions
- Priority rankings (High/Medium/Low)
- Source references
""",
                "input_schema": {
                    "gap_analysis": "List[MarketGap] - Market gaps from analysis",
                    "company_context": "Company - Company profile data"
                },
                "request_model": "InferredFromGaps",
                "response_model": OpportunityResponse,
                "next_agent": "Report Synthesis Agent"
            },
            "Report Synthesis Agent": {
                "description": """
## Report Synthesis Agent

**Purpose:** Compile comprehensive final research report.

**Key Functions:**
- Data synthesis and integration
- Executive summary creation
- Strategic recommendation compilation
- Final report generation

**Input Requirements:**
- All previous agent outputs
- Complete analysis chain results

**Output Format:**
- Executive summary
- Comprehensive findings report
- Strategic recommendations
- Complete data synthesis
""",
                "input_schema": {
                    "company_research_data": "Company - Company research results",
                    "domain_research_data": "List[IndustryOpportunity] - Industry analysis",
                    "market_research_data": "MarketData - Market data results",
                    "competitive_research_data": "List[CompetitiveLandscape] - Competitive analysis",
                    "gap_analysis_data": "List[MarketGap] - Gap analysis results",
                    "opportunity_research_data": "List[Opportunity] - Opportunity analysis"
                },
                "request_model": ReportSynthesisRequest,
                "response_model": ReportSynthesisResponse,
                "next_agent": None
            }
        }
    
    def _create_output_display(self, agent_name: str) -> Text:
        """Create styled output display for the agent with scrolling support"""
        if agent_name not in self.agent_outputs:
            return Text("No output available yet.\nRun the agent to generate output.\n\n[V] View Full Output (when available)", style="dim")
        
        output = self.agent_outputs[agent_name]
        
        # Validate output first
        validation_result = self._validate_output(agent_name, output)
        
        content = Text()
        
        # Status header
        content.append("Output Status: ", style="bold")
        if validation_result["is_valid"]:
            content.append("✓ Valid\n\n", style="bold green")
        else:
            content.append("✗ Invalid\n", style="bold red")
            content.append(f"Issues: {', '.join(validation_result['issues'])}\n\n", style="yellow")
        
        # Check if we have data to display
        if not output.get("success") or not output.get("data"):
            content.append("Error: ", style="bold red")
            content.append(f"{output.get('error', 'Unknown error')}\n", style="red")
            return content
        
        # Stylized data display based on agent type
        styled_output = self._create_styled_data_display(agent_name, output["data"])
        
        # Handle scrolling for long outputs
        output_lines = styled_output.split('\n')
        total_lines = len(output_lines)
        
        if total_lines <= self.output_lines_per_page:
            # Show all content if it fits
            content.append(styled_output, style="cyan")
            content.append("\n\n[V] View Raw JSON", style="dim")
        else:
            # Show paginated content
            start_line = self.output_scroll_offset
            end_line = min(start_line + self.output_lines_per_page, total_lines)
            
            visible_lines = output_lines[start_line:end_line]
            content.append('\n'.join(visible_lines), style="cyan")
            
            # Add scroll indicators
            content.append(f"\n\n--- Page {start_line//self.output_lines_per_page + 1}/{(total_lines-1)//self.output_lines_per_page + 1} ---", style="bold yellow")
            content.append("\n[↑/↓] Scroll  [V] View Raw JSON  [R] Reset Scroll", style="dim")
        
        return content
    
    def _create_styled_data_display(self, agent_name: str, data: Any) -> str:
        """Create stylized display for agent data based on agent type"""
        try:
            if agent_name == "Company Research Agent":
                return self._style_company_data(data)
            elif agent_name == "Industry Analysis Agent":
                return self._style_industry_data(data)
            elif agent_name == "Market Data Agent":
                return self._style_market_data(data)
            elif agent_name == "Competitive Landscape Agent":
                return self._style_competitive_data(data)
            elif agent_name == "Market Gap Analysis Agent":
                return self._style_gap_analysis_data(data)
            elif agent_name == "Opportunity Agent":
                return self._style_opportunity_data(data)
            elif agent_name == "Report Synthesis Agent":
                return self._style_report_data(data)
            else:
                return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error displaying data: {str(e)}\n\nRaw data:\n{json.dumps(data, indent=2)}"
    
    def _style_company_data(self, data: Dict) -> str:
        """Style company research data"""
        output = f"🏢 COMPANY PROFILE\n{'='*50}\n\n"
        output += f"Name: {data.get('name', 'N/A')}\n"
        output += f"Industry: {data.get('industry', 'N/A')}\n"
        output += f"Location: {data.get('headquarters', 'N/A')}\n\n"
        
        output += f"Description:\n{data.get('description', 'N/A')}\n\n"
        
        products = data.get('products', [])
        if products:
            output += f"Products & Services ({len(products)}):\n"
            for i, product in enumerate(products, 1):
                output += f"  {i}. {product}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nSources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_industry_data(self, data: List[Dict]) -> str:
        """Style industry analysis data"""
        output = f"🎯 INDUSTRY OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Sort by score descending
        sorted_data = sorted(data, key=lambda x: x.get('score', 0), reverse=True)
        
        for i, opp in enumerate(sorted_data, 1):
            score = opp.get('score', 0)
            score_bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            
            output += f"{i}. {opp.get('domain', 'Unknown Domain')}\n"
            output += f"   Score: {score:.2f} [{score_bar}]\n"
            output += f"   Rationale: {opp.get('rationale', 'No rationale provided')}\n"
            
            sources = opp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:3])}"
                if len(sources) > 3:
                    output += f" (+{len(sources)-3} more)"
            output += "\n\n"
        
        return output
    
    def _style_market_data(self, data: Dict) -> str:
        """Style market data"""
        output = f"📊 MARKET STATISTICS\n{'='*50}\n\n"
        
        market_size = data.get('market_size_usd', 0)
        if market_size >= 1_000_000_000:
            size_display = f"${market_size/1_000_000_000:.1f}B USD"
        elif market_size >= 1_000_000:
            size_display = f"${market_size/1_000_000:.1f}M USD"
        else:
            size_display = f"${market_size:,.0f} USD"
        
        output += f"Market Size: {size_display}\n"
        
        cagr = data.get('CAGR', 0)
        cagr_percent = cagr * 100 if cagr < 1 else cagr
        output += f"Growth Rate (CAGR): {cagr_percent:.1f}%\n\n"
        
        drivers = data.get('key_drivers', [])
        if drivers:
            output += f"Key Market Drivers ({len(drivers)}):\n"
            for i, driver in enumerate(drivers, 1):
                output += f"  {i}. {driver}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nData Sources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_competitive_data(self, data: List[Dict]) -> str:
        """Style competitive landscape data"""
        output = f"🏆 COMPETITIVE LANDSCAPE\n{'='*50}\n\n"
        
        if not data:
            return output + "No competitors identified."
        
        # Sort by market share descending
        sorted_data = sorted(data, key=lambda x: x.get('market_share', 0), reverse=True)
        
        for i, comp in enumerate(sorted_data, 1):
            market_share = comp.get('market_share', 0)
            share_bar = "█" * int(market_share * 20) + "░" * max(0, 20 - int(market_share * 20))
            
            output += f"{i}. {comp.get('competitor', 'Unknown Company')}\n"
            output += f"   Product: {comp.get('product', 'N/A')}\n"
            output += f"   Market Share: {market_share:.1%} [{share_bar}]\n"
            output += f"   Position: {comp.get('note', 'No information available')}\n"
            
            sources = comp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:2])}"
                if len(sources) > 2:
                    output += f" (+{len(sources)-2} more)"
            output += "\n\n"
        
        return output
    
    def _style_gap_analysis_data(self, data: List[Dict]) -> str:
        """Style market gap analysis data"""
        output = f"🔍 MARKET GAP ANALYSIS\n{'='*50}\n\n"
        
        if not data:
            return output + "No market gaps identified."
        
        # Group by impact level
        high_impact = [gap for gap in data if gap.get('impact', '').lower() == 'high']
        medium_impact = [gap for gap in data if gap.get('impact', '').lower() == 'medium']
        low_impact = [gap for gap in data if gap.get('impact', '').lower() == 'low']
        
        for impact_level, gaps, emoji in [
            ('HIGH IMPACT', high_impact, '🔥'),
            ('MEDIUM IMPACT', medium_impact, '⚡'),
            ('LOW IMPACT', low_impact, '💡')
        ]:
            if gaps:
                output += f"{emoji} {impact_level} GAPS ({len(gaps)})\n{'-'*30}\n"
                for i, gap in enumerate(gaps, 1):
                    output += f"{i}. {gap.get('gap', 'Unknown gap')}\n"
                    output += f"   Evidence: {gap.get('evidence', 'No evidence provided')}\n"
                    source = gap.get('source', 'No source')
                    output += f"   Source: {source}\n\n"
        
        return output
    
    def _style_opportunity_data(self, data: List[Dict]) -> str:
        """Style opportunity data"""
        output = f"💰 BUSINESS OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Group by priority
        high_priority = [opp for opp in data if opp.get('priority', '').lower() == 'high']
        medium_priority = [opp for opp in data if opp.get('priority', '').lower() == 'medium']
        low_priority = [opp for opp in data if opp.get('priority', '').lower() == 'low']
        
        for priority_level, opps, emoji in [
            ('HIGH PRIORITY', high_priority, '🚀'),
            ('MEDIUM PRIORITY', medium_priority, '⭐'),
            ('LOW PRIORITY', low_priority, '💼')
        ]:
            if opps:
                output += f"{emoji} {priority_level} OPPORTUNITIES ({len(opps)})\n{'-'*35}\n"
                for i, opp in enumerate(opps, 1):
                    output += f"{i}. {opp.get('title', 'Unknown opportunity')}\n"
                    output += f"   Description: {opp.get('description', 'No description provided')}\n"
                    sources = opp.get('sources', [])
                    if sources:
                        output += f"   Sources: {', '.join(sources[:2])}"
                        if len(sources) > 2:
                            output += f" (+{len(sources)-2} more)"
                    output += "\n\n"
        
        return output
    
    def _style_report_data(self, data: Dict) -> str:
        """Style report synthesis data"""
        output = f"📋 SYNTHESIS REPORT\n{'='*50}\n\n"
        
        output += f"Report Title: {data.get('report_title', 'N/A')}\n"
        output += f"Generated: {data.get('generated_at', 'N/A')}\n"
        
        pdf_content = data.get('pdf_content', b'')
        if isinstance(pdf_content, bytes):
            output += f"PDF Size: {len(pdf_content):,} bytes\n"
        elif isinstance(pdf_content, str):
            output += f"Content Length: {len(pdf_content):,} characters\n"
        
        is_placeholder = data.get('placeholder', False)
        if is_placeholder:
            output += "Status: 📋 Placeholder Implementation\n"
        else:
            output += "Status: ✅ Production Report\n"
        
        output += "\nThe comprehensive research report has been generated and is ready for download."
        
        return output

    def _get_user_input(self) -> str:
        """Get user input for navigation"""
        key = self.console.input("")
        
        if key.lower() in ['q', 'quit']:
            return "quit"
        elif key.lower() in ['r', 'run']:
            return "run"
        elif key.lower() in ['c', 'chain']:
            return "chain"
        elif key.lower() == 'w':  # Navigate up in agent list
            return "prev"
        elif key.lower() == 's':  # Navigate down in agent list
            return "next"
        elif key.lower() == 'a':  # Navigate left in tabs
            return "tab_prev"
        elif key.lower() == 'd':  # Navigate right in tabs
            return "tab_next"
        elif key == '':  # Enter
            return "run"
        elif key.lower() == 'v':  # View full output
            return "view_full"
        elif key in ['↑', 'up']:  # Scroll up
            return "scroll_up"
        elif key in ['↓', 'down']:  # Scroll down
            return "scroll_down"
        else:
            return "invalid"
    
    def run(self):
        """Main runner interface with two-panel layout"""
        while True:
            try:
                self._show_interface()
                choice = self._get_user_input()
                
                if choice == "quit":
                    break
                elif choice == "run":
                    self._run_current_agent()
                elif choice == "next":
                    self._move_to_next_agent()
                elif choice == "prev":
                    self._move_to_previous_agent()
                elif choice == "tab_prev":
                    self._switch_tab_prev()
                elif choice == "tab_next":
                    self._switch_tab_next()
                elif choice == "chain":
                    self._run_agent_chain()
                elif choice == "reset":
                    self._reset_outputs()
                elif choice == "view_full":
                    self._show_full_output()
                elif choice == "scroll_up":
                    self._scroll_output_up()
                elif choice == "scroll_down":
                    self._scroll_output_down()
                    
            except KeyboardInterrupt:
                break
    
    def _scroll_output_up(self):
        """Scroll output up"""
        if self.current_tab == "output":
            self.output_scroll_offset = max(0, self.output_scroll_offset - 5)
    
    def _scroll_output_down(self):
        """Scroll output down"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                output = self.agent_outputs[current_agent_name]
                if output.get("success") and output.get("data"):
                    styled_output = self._create_styled_data_display(current_agent_name, output["data"])
                    total_lines = len(styled_output.split('\n'))
                    max_offset = max(0, total_lines - self.output_lines_per_page)
                    self.output_scroll_offset = min(max_offset, self.output_scroll_offset + 5)
    
    def _show_full_output(self):
        """Show full JSON output in a separate view"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                self.console.clear()
                output = self.agent_outputs[current_agent_name]
                
                self.console.print(f"\n[bold blue]Full Output - {current_agent_name}[/bold blue]")
                self.console.print("=" * 60)
                
                # Show raw JSON with syntax highlighting
                json_content = json.dumps(output, indent=2)
                syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
                self.console.print(syntax)
                
                self.console.print("\n[dim]Press Enter to return to main view...[/dim]")
                input()
                self.output_scroll_offset = 0  # Reset scroll when returning

    def _create_tab_header(self) -> Panel:
        """Create tab header"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == self.current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output tab
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if (current_agent_name in self.agent_outputs and 
                self.agent_outputs[current_agent_name].get("success")):
                tabs.append("[dim]| [↑/↓] Scroll [V] Full View[/dim]")
        
        return Panel(" ".join(tabs), style="yellow")
    
    def _show_interface(self):
        """Display the two-panel interface"""
        self.console.clear()
        
        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        # Left panel - Agent selection
        layout["left"].update(self._create_agent_list_panel())
        
        # Right panel - Tabbed content
        layout["right"].split_column(
            Layout(self._create_tab_header(), size=3),
            Layout(self._create_tab_content())
        )
        
        self.console.print(layout)
    
    def _create_agent_list_panel(self) -> Panel:
        """Create the left panel with agent selection"""
        agent_list = Table(show_header=False, box=None)
        agent_list.add_column("", style="cyan")
        
        for i, (agent_name, _) in enumerate(self.agents.items()):
            if i == self.current_agent_index:
                agent_list.add_row(f"▶ {agent_name}", style="bold green")
            else:
                status = "✓" if agent_name in self.agent_outputs else "○"
                agent_list.add_row(f"{status} {agent_name}")
        
        controls = Text("\nControls:", style="bold")
        controls.append("\n[W/S] Navigate Agents", style="dim")
        controls.append("\n[A/D] Navigate Tabs", style="dim")
        controls.append("\n[Enter/R] Run Agent", style="dim")
        controls.append("\n[C] Run Chain", style="dim")
        controls.append("\n[Q] Quit", style="dim")
        
        content = Columns([agent_list, controls])
        return Panel(content, title="Agent Selection", style="blue")
    
    def _create_tab_header(self) -> Panel:
        """Create tab header"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == self.current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output tab
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if (current_agent_name in self.agent_outputs and 
                self.agent_outputs[current_agent_name].get("success")):
                tabs.append("[dim]| [↑/↓] Scroll [V] Full View[/dim]")
        
        return Panel(" ".join(tabs), style="yellow")
    
    def _create_tab_content(self) -> Panel:
        """Create content for the current tab"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        agent_def = self.agents[current_agent_name]
        
        if self.current_tab == "description":
            content = Markdown(agent_def["description"])
            return Panel(content, title=f"{current_agent_name} - Description")
        
        elif self.current_tab == "input":
            content = self._create_input_form(current_agent_name, agent_def)
            return Panel(content, title=f"{current_agent_name} - Input")
        
        elif self.current_tab == "output":
            content = self._create_output_display(current_agent_name)
            return Panel(content, title=f"{current_agent_name} - Output")
        
        return Panel("Unknown tab", style="red")
    
    def _create_input_form(self, agent_name: str, agent_def: Dict) -> Text:
        """Create input form for the agent"""
        form = Text("Input Requirements:\n\n", style="bold")
        
        # Check if we have previous agent output to use
        prev_agent_output = self._get_previous_agent_output(agent_name)
        
        for field, description in agent_def["input_schema"].items():
            form.append(f"{field}: ", style="cyan")
            form.append(f"{description}\n", style="dim")
            
            # Show if data is available from previous agent
            if prev_agent_output and field.lower() in [k.lower() for k in prev_agent_output.keys()]:
                form.append("  ✓ Available from previous agent\n", style="green")
            else:
                form.append("  ⚠ Requires manual input\n", style="yellow")
            form.append("\n")
        
        if prev_agent_output:
            form.append("\nPrevious Agent Output Available:", style="bold green")
            form.append(f"\n{json.dumps(prev_agent_output, indent=2)[:200]}...", style="dim")
        
        return form
    
    def _create_output_display(self, agent_name: str) -> Text:
        """Create styled output display for the agent with scrolling support"""
        if agent_name not in self.agent_outputs:
            return Text("No output available yet.\nRun the agent to generate output.\n\n[V] View Full Output (when available)", style="dim")
        
        output = self.agent_outputs[agent_name]
        
        # Validate output first
        validation_result = self._validate_output(agent_name, output)
        
        content = Text()
        
        # Status header
        content.append("Output Status: ", style="bold")
        if validation_result["is_valid"]:
            content.append("✓ Valid\n\n", style="bold green")
        else:
            content.append("✗ Invalid\n", style="bold red")
            content.append(f"Issues: {', '.join(validation_result['issues'])}\n\n", style="yellow")
        
        # Check if we have data to display
        if not output.get("success") or not output.get("data"):
            content.append("Error: ", style="bold red")
            content.append(f"{output.get('error', 'Unknown error')}\n", style="red")
            return content
        
        # Stylized data display based on agent type
        styled_output = self._create_styled_data_display(agent_name, output["data"])
        
        # Handle scrolling for long outputs
        output_lines = styled_output.split('\n')
        total_lines = len(output_lines)
        
        if total_lines <= self.output_lines_per_page:
            # Show all content if it fits
            content.append(styled_output, style="cyan")
            content.append("\n\n[V] View Raw JSON", style="dim")
        else:
            # Show paginated content
            start_line = self.output_scroll_offset
            end_line = min(start_line + self.output_lines_per_page, total_lines)
            
            visible_lines = output_lines[start_line:end_line]
            content.append('\n'.join(visible_lines), style="cyan")
            
            # Add scroll indicators
            content.append(f"\n\n--- Page {start_line//self.output_lines_per_page + 1}/{(total_lines-1)//self.output_lines_per_page + 1} ---", style="bold yellow")
            content.append("\n[↑/↓] Scroll  [V] View Raw JSON  [R] Reset Scroll", style="dim")
        
        return content
    
    def _create_styled_data_display(self, agent_name: str, data: Any) -> str:
        """Create stylized display for agent data based on agent type"""
        try:
            if agent_name == "Company Research Agent":
                return self._style_company_data(data)
            elif agent_name == "Industry Analysis Agent":
                return self._style_industry_data(data)
            elif agent_name == "Market Data Agent":
                return self._style_market_data(data)
            elif agent_name == "Competitive Landscape Agent":
                return self._style_competitive_data(data)
            elif agent_name == "Market Gap Analysis Agent":
                return self._style_gap_analysis_data(data)
            elif agent_name == "Opportunity Agent":
                return self._style_opportunity_data(data)
            elif agent_name == "Report Synthesis Agent":
                return self._style_report_data(data)
            else:
                return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error displaying data: {str(e)}\n\nRaw data:\n{json.dumps(data, indent=2)}"
    
    def _style_company_data(self, data: Dict) -> str:
        """Style company research data"""
        output = f"🏢 COMPANY PROFILE\n{'='*50}\n\n"
        output += f"Name: {data.get('name', 'N/A')}\n"
        output += f"Industry: {data.get('industry', 'N/A')}\n"
        output += f"Location: {data.get('headquarters', 'N/A')}\n\n"
        
        output += f"Description:\n{data.get('description', 'N/A')}\n\n"
        
        products = data.get('products', [])
        if products:
            output += f"Products & Services ({len(products)}):\n"
            for i, product in enumerate(products, 1):
                output += f"  {i}. {product}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nSources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_industry_data(self, data: List[Dict]) -> str:
        """Style industry analysis data"""
        output = f"🎯 INDUSTRY OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Sort by score descending
        sorted_data = sorted(data, key=lambda x: x.get('score', 0), reverse=True)
        
        for i, opp in enumerate(sorted_data, 1):
            score = opp.get('score', 0)
            score_bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            
            output += f"{i}. {opp.get('domain', 'Unknown Domain')}\n"
            output += f"   Score: {score:.2f} [{score_bar}]\n"
            output += f"   Rationale: {opp.get('rationale', 'No rationale provided')}\n"
            
            sources = opp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:3])}"
                if len(sources) > 3:
                    output += f" (+{len(sources)-3} more)"
            output += "\n\n"
        
        return output
    
    def _style_market_data(self, data: Dict) -> str:
        """Style market data"""
        output = f"📊 MARKET STATISTICS\n{'='*50}\n\n"
        
        market_size = data.get('market_size_usd', 0)
        if market_size >= 1_000_000_000:
            size_display = f"${market_size/1_000_000_000:.1f}B USD"
        elif market_size >= 1_000_000:
            size_display = f"${market_size/1_000_000:.1f}M USD"
        else:
            size_display = f"${market_size:,.0f} USD"
        
        output += f"Market Size: {size_display}\n"
        
        cagr = data.get('CAGR', 0)
        cagr_percent = cagr * 100 if cagr < 1 else cagr
        output += f"Growth Rate (CAGR): {cagr_percent:.1f}%\n\n"
        
        drivers = data.get('key_drivers', [])
        if drivers:
            output += f"Key Market Drivers ({len(drivers)}):\n"
            for i, driver in enumerate(drivers, 1):
                output += f"  {i}. {driver}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nData Sources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_competitive_data(self, data: List[Dict]) -> str:
        """Style competitive landscape data"""
        output = f"🏆 COMPETITIVE LANDSCAPE\n{'='*50}\n\n"
        
        if not data:
            return output + "No competitors identified."
        
        # Sort by market share descending
        sorted_data = sorted(data, key=lambda x: x.get('market_share', 0), reverse=True)
        
        for i, comp in enumerate(sorted_data, 1):
            market_share = comp.get('market_share', 0)
            share_bar = "█" * int(market_share * 20) + "░" * max(0, 20 - int(market_share * 20))
            
            output += f"{i}. {comp.get('competitor', 'Unknown Company')}\n"
            output += f"   Product: {comp.get('product', 'N/A')}\n"
            output += f"   Market Share: {market_share:.1%} [{share_bar}]\n"
            output += f"   Position: {comp.get('note', 'No information available')}\n"
            
            sources = comp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:2])}"
                if len(sources) > 2:
                    output += f" (+{len(sources)-2} more)"
            output += "\n\n"
        
        return output
    
    def _style_gap_analysis_data(self, data: List[Dict]) -> str:
        """Style market gap analysis data"""
        output = f"🔍 MARKET GAP ANALYSIS\n{'='*50}\n\n"
        
        if not data:
            return output + "No market gaps identified."
        
        # Group by impact level
        high_impact = [gap for gap in data if gap.get('impact', '').lower() == 'high']
        medium_impact = [gap for gap in data if gap.get('impact', '').lower() == 'medium']
        low_impact = [gap for gap in data if gap.get('impact', '').lower() == 'low']
        
        for impact_level, gaps, emoji in [
            ('HIGH IMPACT', high_impact, '🔥'),
            ('MEDIUM IMPACT', medium_impact, '⚡'),
            ('LOW IMPACT', low_impact, '💡')
        ]:
            if gaps:
                output += f"{emoji} {impact_level} GAPS ({len(gaps)})\n{'-'*30}\n"
                for i, gap in enumerate(gaps, 1):
                    output += f"{i}. {gap.get('gap', 'Unknown gap')}\n"
                    output += f"   Evidence: {gap.get('evidence', 'No evidence provided')}\n"
                    source = gap.get('source', 'No source')
                    output += f"   Source: {source}\n\n"
        
        return output
    
    def _style_opportunity_data(self, data: List[Dict]) -> str:
        """Style opportunity data"""
        output = f"💰 BUSINESS OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Group by priority
        high_priority = [opp for opp in data if opp.get('priority', '').lower() == 'high']
        medium_priority = [opp for opp in data if opp.get('priority', '').lower() == 'medium']
        low_priority = [opp for opp in data if opp.get('priority', '').lower() == 'low']
        
        for priority_level, opps, emoji in [
            ('HIGH PRIORITY', high_priority, '🚀'),
            ('MEDIUM PRIORITY', medium_priority, '⭐'),
            ('LOW PRIORITY', low_priority, '💼')
        ]:
            if opps:
                output += f"{emoji} {priority_level} OPPORTUNITIES ({len(opps)})\n{'-'*35}\n"
                for i, opp in enumerate(opps, 1):
                    output += f"{i}. {opp.get('title', 'Unknown opportunity')}\n"
                    output += f"   Description: {opp.get('description', 'No description provided')}\n"
                    sources = opp.get('sources', [])
                    if sources:
                        output += f"   Sources: {', '.join(sources[:2])}"
                        if len(sources) > 2:
                            output += f" (+{len(sources)-2} more)"
                    output += "\n\n"
        
        return output
    
    def _style_report_data(self, data: Dict) -> str:
        """Style report synthesis data"""
        output = f"📋 SYNTHESIS REPORT\n{'='*50}\n\n"
        
        output += f"Report Title: {data.get('report_title', 'N/A')}\n"
        output += f"Generated: {data.get('generated_at', 'N/A')}\n"
        
        pdf_content = data.get('pdf_content', b'')
        if isinstance(pdf_content, bytes):
            output += f"PDF Size: {len(pdf_content):,} bytes\n"
        elif isinstance(pdf_content, str):
            output += f"Content Length: {len(pdf_content):,} characters\n"
        
        is_placeholder = data.get('placeholder', False)
        if is_placeholder:
            output += "Status: 📋 Placeholder Implementation\n"
        else:
            output += "Status: ✅ Production Report\n"
        
        output += "\nThe comprehensive research report has been generated and is ready for download."
        
        return output

    def _get_user_input(self) -> str:
        """Get user input for navigation"""
        key = self.console.input("")
        
        if key.lower() in ['q', 'quit']:
            return "quit"
        elif key.lower() in ['r', 'run']:
            return "run"
        elif key.lower() in ['c', 'chain']:
            return "chain"
        elif key.lower() == 'w':  # Navigate up in agent list
            return "prev"
        elif key.lower() == 's':  # Navigate down in agent list
            return "next"
        elif key.lower() == 'a':  # Navigate left in tabs
            return "tab_prev"
        elif key.lower() == 'd':  # Navigate right in tabs
            return "tab_next"
        elif key == '':  # Enter
            return "run"
        elif key.lower() == 'v':  # View full output
            return "view_full"
        elif key in ['↑', 'up']:  # Scroll up
            return "scroll_up"
        elif key in ['↓', 'down']:  # Scroll down
            return "scroll_down"
        else:
            return "invalid"
    
    def run(self):
        """Main runner interface with two-panel layout"""
        while True:
            try:
                self._show_interface()
                choice = self._get_user_input()
                
                if choice == "quit":
                    break
                elif choice == "run":
                    self._run_current_agent()
                elif choice == "next":
                    self._move_to_next_agent()
                elif choice == "prev":
                    self._move_to_previous_agent()
                elif choice == "tab_prev":
                    self._switch_tab_prev()
                elif choice == "tab_next":
                    self._switch_tab_next()
                elif choice == "chain":
                    self._run_agent_chain()
                elif choice == "reset":
                    self._reset_outputs()
                elif choice == "view_full":
                    self._show_full_output()
                elif choice == "scroll_up":
                    self._scroll_output_up()
                elif choice == "scroll_down":
                    self._scroll_output_down()
                    
            except KeyboardInterrupt:
                break
    
    def _scroll_output_up(self):
        """Scroll output up"""
        if self.current_tab == "output":
            self.output_scroll_offset = max(0, self.output_scroll_offset - 5)
    
    def _scroll_output_down(self):
        """Scroll output down"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                output = self.agent_outputs[current_agent_name]
                if output.get("success") and output.get("data"):
                    styled_output = self._create_styled_data_display(current_agent_name, output["data"])
                    total_lines = len(styled_output.split('\n'))
                    max_offset = max(0, total_lines - self.output_lines_per_page)
                    self.output_scroll_offset = min(max_offset, self.output_scroll_offset + 5)
    
    def _show_full_output(self):
        """Show full JSON output in a separate view"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                self.console.clear()
                output = self.agent_outputs[current_agent_name]
                
                self.console.print(f"\n[bold blue]Full Output - {current_agent_name}[/bold blue]")
                self.console.print("=" * 60)
                
                # Show raw JSON with syntax highlighting
                json_content = json.dumps(output, indent=2)
                syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
                self.console.print(syntax)
                
                self.console.print("\n[dim]Press Enter to return to main view...[/dim]")
                input()
                self.output_scroll_offset = 0  # Reset scroll when returning

    def _create_tab_header(self) -> Panel:
        """Create tab header"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == self.current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output tab
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if (current_agent_name in self.agent_outputs and 
                self.agent_outputs[current_agent_name].get("success")):
                tabs.append("[dim]| [↑/↓] Scroll [V] Full View[/dim]")
        
        return Panel(" ".join(tabs), style="yellow")
    
    def _show_interface(self):
        """Display the two-panel interface"""
        self.console.clear()
        
        layout = Layout()
        layout.split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        # Left panel - Agent selection
        layout["left"].update(self._create_agent_list_panel())
        
        # Right panel - Tabbed content
        layout["right"].split_column(
            Layout(self._create_tab_header(), size=3),
            Layout(self._create_tab_content())
        )
        
        self.console.print(layout)
    
    def _create_agent_list_panel(self) -> Panel:
        """Create the left panel with agent selection"""
        agent_list = Table(show_header=False, box=None)
        agent_list.add_column("", style="cyan")
        
        for i, (agent_name, _) in enumerate(self.agents.items()):
            if i == self.current_agent_index:
                agent_list.add_row(f"▶ {agent_name}", style="bold green")
            else:
                status = "✓" if agent_name in self.agent_outputs else "○"
                agent_list.add_row(f"{status} {agent_name}")
        
        controls = Text("\nControls:", style="bold")
        controls.append("\n[W/S] Navigate Agents", style="dim")
        controls.append("\n[A/D] Navigate Tabs", style="dim")
        controls.append("\n[Enter/R] Run Agent", style="dim")
        controls.append("\n[C] Run Chain", style="dim")
        controls.append("\n[Q] Quit", style="dim")
        
        content = Columns([agent_list, controls])
        return Panel(content, title="Agent Selection", style="blue")
    
    def _create_tab_header(self) -> Panel:
        """Create tab header"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == self.current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output tab
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if (current_agent_name in self.agent_outputs and 
                self.agent_outputs[current_agent_name].get("success")):
                tabs.append("[dim]| [↑/↓] Scroll [V] Full View[/dim]")
        
        return Panel(" ".join(tabs), style="yellow")
    
    def _create_tab_content(self) -> Panel:
        """Create content for the current tab"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        agent_def = self.agents[current_agent_name]
        
        if self.current_tab == "description":
            content = Markdown(agent_def["description"])
            return Panel(content, title=f"{current_agent_name} - Description")
        
        elif self.current_tab == "input":
            content = self._create_input_form(current_agent_name, agent_def)
            return Panel(content, title=f"{current_agent_name} - Input")
        
        elif self.current_tab == "output":
            content = self._create_output_display(current_agent_name)
            return Panel(content, title=f"{current_agent_name} - Output")
        
        return Panel("Unknown tab", style="red")
    
    def _create_input_form(self, agent_name: str, agent_def: Dict) -> Text:
        """Create input form for the agent"""
        form = Text("Input Requirements:\n\n", style="bold")
        
        # Check if we have previous agent output to use
        prev_agent_output = self._get_previous_agent_output(agent_name)
        
        for field, description in agent_def["input_schema"].items():
            form.append(f"{field}: ", style="cyan")
            form.append(f"{description}\n", style="dim")
            
            # Show if data is available from previous agent
            if prev_agent_output and field.lower() in [k.lower() for k in prev_agent_output.keys()]:
                form.append("  ✓ Available from previous agent\n", style="green")
            else:
                form.append("  ⚠ Requires manual input\n", style="yellow")
            form.append("\n")
        
        if prev_agent_output:
            form.append("\nPrevious Agent Output Available:", style="bold green")
            form.append(f"\n{json.dumps(prev_agent_output, indent=2)[:200]}...", style="dim")
        
        return form
    
    def _create_output_display(self, agent_name: str) -> Text:
        """Create styled output display for the agent with scrolling support"""
        if agent_name not in self.agent_outputs:
            return Text("No output available yet.\nRun the agent to generate output.\n\n[V] View Full Output (when available)", style="dim")
        
        output = self.agent_outputs[agent_name]
        
        # Validate output first
        validation_result = self._validate_output(agent_name, output)
        
        content = Text()
        
        # Status header
        content.append("Output Status: ", style="bold")
        if validation_result["is_valid"]:
            content.append("✓ Valid\n\n", style="bold green")
        else:
            content.append("✗ Invalid\n", style="bold red")
            content.append(f"Issues: {', '.join(validation_result['issues'])}\n\n", style="yellow")
        
        # Check if we have data to display
        if not output.get("success") or not output.get("data"):
            content.append("Error: ", style="bold red")
            content.append(f"{output.get('error', 'Unknown error')}\n", style="red")
            return content
        
        # Stylized data display based on agent type
        styled_output = self._create_styled_data_display(agent_name, output["data"])
        
        # Handle scrolling for long outputs
        output_lines = styled_output.split('\n')
        total_lines = len(output_lines)
        
        if total_lines <= self.output_lines_per_page:
            # Show all content if it fits
            content.append(styled_output, style="cyan")
            content.append("\n\n[V] View Raw JSON", style="dim")
        else:
            # Show paginated content
            start_line = self.output_scroll_offset
            end_line = min(start_line + self.output_lines_per_page, total_lines)
            
            visible_lines = output_lines[start_line:end_line]
            content.append('\n'.join(visible_lines), style="cyan")
            
            # Add scroll indicators
            content.append(f"\n\n--- Page {start_line//self.output_lines_per_page + 1}/{(total_lines-1)//self.output_lines_per_page + 1} ---", style="bold yellow")
            content.append("\n[↑/↓] Scroll  [V] View Raw JSON  [R] Reset Scroll", style="dim")
        
        return content
    
    def _create_styled_data_display(self, agent_name: str, data: Any) -> str:
        """Create stylized display for agent data based on agent type"""
        try:
            if agent_name == "Company Research Agent":
                return self._style_company_data(data)
            elif agent_name == "Industry Analysis Agent":
                return self._style_industry_data(data)
            elif agent_name == "Market Data Agent":
                return self._style_market_data(data)
            elif agent_name == "Competitive Landscape Agent":
                return self._style_competitive_data(data)
            elif agent_name == "Market Gap Analysis Agent":
                return self._style_gap_analysis_data(data)
            elif agent_name == "Opportunity Agent":
                return self._style_opportunity_data(data)
            elif agent_name == "Report Synthesis Agent":
                return self._style_report_data(data)
            else:
                return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error displaying data: {str(e)}\n\nRaw data:\n{json.dumps(data, indent=2)}"
    
    def _style_company_data(self, data: Dict) -> str:
        """Style company research data"""
        output = f"🏢 COMPANY PROFILE\n{'='*50}\n\n"
        output += f"Name: {data.get('name', 'N/A')}\n"
        output += f"Industry: {data.get('industry', 'N/A')}\n"
        output += f"Location: {data.get('headquarters', 'N/A')}\n\n"
        
        output += f"Description:\n{data.get('description', 'N/A')}\n\n"
        
        products = data.get('products', [])
        if products:
            output += f"Products & Services ({len(products)}):\n"
            for i, product in enumerate(products, 1):
                output += f"  {i}. {product}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nSources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_industry_data(self, data: List[Dict]) -> str:
        """Style industry analysis data"""
        output = f"🎯 INDUSTRY OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Sort by score descending
        sorted_data = sorted(data, key=lambda x: x.get('score', 0), reverse=True)
        
        for i, opp in enumerate(sorted_data, 1):
            score = opp.get('score', 0)
            score_bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            
            output += f"{i}. {opp.get('domain', 'Unknown Domain')}\n"
            output += f"   Score: {score:.2f} [{score_bar}]\n"
            output += f"   Rationale: {opp.get('rationale', 'No rationale provided')}\n"
            
            sources = opp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:3])}"
                if len(sources) > 3:
                    output += f" (+{len(sources)-3} more)"
            output += "\n\n"
        
        return output
    
    def _style_market_data(self, data: Dict) -> str:
        """Style market data"""
        output = f"📊 MARKET STATISTICS\n{'='*50}\n\n"
        
        market_size = data.get('market_size_usd', 0)
        if market_size >= 1_000_000_000:
            size_display = f"${market_size/1_000_000_000:.1f}B USD"
        elif market_size >= 1_000_000:
            size_display = f"${market_size/1_000_000:.1f}M USD"
        else:
            size_display = f"${market_size:,.0f} USD"
        
        output += f"Market Size: {size_display}\n"
        
        cagr = data.get('CAGR', 0)
        cagr_percent = cagr * 100 if cagr < 1 else cagr
        output += f"Growth Rate (CAGR): {cagr_percent:.1f}%\n\n"
        
        drivers = data.get('key_drivers', [])
        if drivers:
            output += f"Key Market Drivers ({len(drivers)}):\n"
            for i, driver in enumerate(drivers, 1):
                output += f"  {i}. {driver}\n"
        
        sources = data.get('sources', [])
        if sources:
            output += f"\nData Sources ({len(sources)}):\n"
            for i, source in enumerate(sources, 1):
                output += f"  {i}. {source}\n"
        
        return output
    
    def _style_competitive_data(self, data: List[Dict]) -> str:
        """Style competitive landscape data"""
        output = f"🏆 COMPETITIVE LANDSCAPE\n{'='*50}\n\n"
        
        if not data:
            return output + "No competitors identified."
        
        # Sort by market share descending
        sorted_data = sorted(data, key=lambda x: x.get('market_share', 0), reverse=True)
        
        for i, comp in enumerate(sorted_data, 1):
            market_share = comp.get('market_share', 0)
            share_bar = "█" * int(market_share * 20) + "░" * max(0, 20 - int(market_share * 20))
            
            output += f"{i}. {comp.get('competitor', 'Unknown Company')}\n"
            output += f"   Product: {comp.get('product', 'N/A')}\n"
            output += f"   Market Share: {market_share:.1%} [{share_bar}]\n"
            output += f"   Position: {comp.get('note', 'No information available')}\n"
            
            sources = comp.get('sources', [])
            if sources:
                output += f"   Sources: {', '.join(sources[:2])}"
                if len(sources) > 2:
                    output += f" (+{len(sources)-2} more)"
            output += "\n\n"
        
        return output
    
    def _style_gap_analysis_data(self, data: List[Dict]) -> str:
        """Style market gap analysis data"""
        output = f"🔍 MARKET GAP ANALYSIS\n{'='*50}\n\n"
        
        if not data:
            return output + "No market gaps identified."
        
        # Group by impact level
        high_impact = [gap for gap in data if gap.get('impact', '').lower() == 'high']
        medium_impact = [gap for gap in data if gap.get('impact', '').lower() == 'medium']
        low_impact = [gap for gap in data if gap.get('impact', '').lower() == 'low']
        
        for impact_level, gaps, emoji in [
            ('HIGH IMPACT', high_impact, '🔥'),
            ('MEDIUM IMPACT', medium_impact, '⚡'),
            ('LOW IMPACT', low_impact, '💡')
        ]:
            if gaps:
                output += f"{emoji} {impact_level} GAPS ({len(gaps)})\n{'-'*30}\n"
                for i, gap in enumerate(gaps, 1):
                    output += f"{i}. {gap.get('gap', 'Unknown gap')}\n"
                    output += f"   Evidence: {gap.get('evidence', 'No evidence provided')}\n"
                    source = gap.get('source', 'No source')
                    output += f"   Source: {source}\n\n"
        
        return output
    
    def _style_opportunity_data(self, data: List[Dict]) -> str:
        """Style opportunity data"""
        output = f"💰 BUSINESS OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Group by priority
        high_priority = [opp for opp in data if opp.get('priority', '').lower() == 'high']
        medium_priority = [opp for opp in data if opp.get('priority', '').lower() == 'medium']
        low_priority = [opp for opp in data if opp.get('priority', '').lower() == 'low']
        
        for priority_level, opps, emoji in [
            ('HIGH PRIORITY', high_priority, '🚀'),
            ('MEDIUM PRIORITY', medium_priority, '⭐'),
            ('LOW PRIORITY', low_priority, '💼')
        ]:
            if opps:
                output += f"{emoji} {priority_level} OPPORTUNITIES ({len(opps)})\n{'-'*35}\n"
                for i, opp in enumerate(opps, 1):
                    output += f"{i}. {opp.get('title', 'Unknown opportunity')}\n"
                    output += f"   Description: {opp.get('description', 'No description provided')}\n"
                    sources = opp.get('sources', [])
                    if sources:
                        output += f"   Sources: {', '.join(sources[:2])}"
                        if len(sources) > 2:
                            output += f" (+{len(sources)-2} more)"
                    output += "\n\n"
        
        return output
    
    def _style_report_data(self, data: Dict) -> str:
        """Style report synthesis data"""
        output = f"📋 SYNTHESIS REPORT\n{'='*50}\n\n"
        
        output += f"Report Title: {data.get('report_title', 'N/A')}\n"
        output += f"Generated: {data.get('generated_at', 'N/A')}\n"
        
        pdf_content = data.get('pdf_content', b'')
        if isinstance(pdf_content, bytes):
            output += f"PDF Size: {len(pdf_content):,} bytes\n"
        elif isinstance(pdf_content, str):
            output += f"Content Length: {len(pdf_content):,} characters\n"
        
        is_placeholder = data.get('placeholder', False)
        if is_placeholder:
            output += "Status: 📋 Placeholder Implementation\n"
        else:
            output += "Status: ✅ Production Report\n"
        
        output += "\nThe comprehensive research report has been generated and is ready for download."
        
        return output

    def _get_user_input(self) -> str:
        """Get user input for navigation"""
        key = self.console.input("")
        
        if key.lower() in ['q', 'quit']:
            return "quit"
        elif key.lower() in ['r', 'run']:
            return "run"
        elif key.lower() in ['c', 'chain']:
            return "chain"
        elif key.lower() == 'w':  # Navigate up in agent list
            return "prev"
        elif key.lower() == 's':  # Navigate down in agent list
            return "next"
        elif key.lower() == 'a':  # Navigate left in tabs
            return "tab_prev"
        elif key.lower() == 'd':  # Navigate right in tabs
            return "tab_next"
        elif key == '':  # Enter
            return "run"
        elif key.lower() == 'v':  # View full output
            return "view_full"
        elif key in ['↑', 'up']:  # Scroll up
            return "scroll_up"
        elif key in ['↓', 'down']:  # Scroll down
            return "scroll_down"
        else:
            return "invalid"
    
    def _run_current_agent(self):
        """Run the currently selected agent"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        
        # Get input from user or previous agent
        agent_input = self._collect_agent_input(current_agent_name)
        
        if agent_input:
            # Simulate agent execution (replace with actual agent call)
            output = self._simulate_agent_execution(current_agent_name, agent_input)
            
            # Validate output
            validation_result = self._validate_output(current_agent_name, output)
            
            if validation_result["is_valid"]:
                self.agent_outputs[current_agent_name] = output
                self.console.print(f"[green]✓ {current_agent_name} completed successfully![/green]")
            else:
                self.console.print(f"[red]✗ {current_agent_name} output validation failed![/red]")
                self.console.print(f"[yellow]Issues: {', '.join(validation_result['issues'])}[/yellow]")
            
            input("Press Enter to continue...")
    
    def _move_to_next_agent(self):
        """Move to the next agent in the list"""
        if self.current_agent_index < len(self.agents) - 1:
            self.current_agent_index += 1
    
    def _move_to_previous_agent(self):
        """Move to the previous agent in the list"""
        if self.current_agent_index > 0:
            self.current_agent_index -= 1
    
    def _switch_tab_next(self):
        """Switch to the next tab"""
        tabs = ["input", "output", "description"]
        current_index = tabs.index(self.current_tab)
        self.current_tab = tabs[(current_index + 1) % len(tabs)]
    
    def _switch_tab_prev(self):
        """Switch to the previous tab"""
        tabs = ["input", "output", "description"]
        current_index = tabs.index(self.current_tab)
        self.current_tab = tabs[(current_index - 1) % len(tabs)]
    
    def _run_agent_chain(self):
        """Run all agents in sequence"""
        self.console.print("[yellow]Running full agent chain...[/yellow]")
        
        # Start from Company Research Agent
        for i, agent_name in enumerate(self.agents.keys()):
            self.current_agent_index = i
            self.console.print(f"[blue]Running {agent_name}...[/blue]")
            
            # Get input for agent
            if agent_name == "Company Research Agent":
                company_name = Prompt.ask("Enter company name for chain execution")
                agent_input = {"company_name": company_name}
            elif agent_name == "Market Data Agent":
                # Use selected domain or prompt for it
                if not self.selected_domain:
                    domain = Prompt.ask("Enter domain for market data analysis")
                else:
                    domain = self.selected_domain
                agent_input = {"domain": domain}
            else:
                agent_input = {"auto_chain": True}
            
            # Run agent
            output = self._simulate_agent_execution(agent_name, agent_input)
            
            # Validate and store output
            validation_result = self._validate_output(agent_name, output)
            if validation_result["is_valid"]:
                self.agent_outputs[agent_name] = output
                self.console.print(f"[green]✓ {agent_name} completed successfully[/green]")
                
                # Handle domain selection after Industry Analysis
                if agent_name == "Industry Analysis Agent" and output.get("success"):
                    self._handle_domain_selection(output.get("data", []))
            else:
                self.console.print(f"[red]✗ {agent_name} failed: {', '.join(validation_result['issues'])}[/red]")
                break
        
        input("Press Enter to continue...")
    
    def _reset_outputs(self):
        """Reset all agent outputs"""
        self.agent_outputs.clear()
        self.selected_domain = None
        self.console.print("[yellow]All outputs reset.[/yellow]")
        input("Press Enter to continue...")
    
    def _get_previous_agent_output(self, agent_name: str) -> Optional[Dict]:
        """Get the output from the previous agent in the chain"""
        agent_list = list(self.agents.keys())
        if agent_name not in agent_list:
            return None
        
        current_index = agent_list.index(agent_name)
        if current_index == 0:
            return None
        
        previous_agent = agent_list[current_index - 1]
        previous_output = self.agent_outputs.get(previous_agent)
        
        if previous_output and previous_output.get("success"):
            return previous_output.get("data")
        
        return None
    
    def _handle_domain_selection(self, industry_opportunities: List[Dict]):
        """Handle domain selection after industry analysis"""
        if not industry_opportunities:
            return
        
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
                    self.selected_domain = industry_opportunities[index].get("domain")
                    self.console.print(f"[green]Selected domain: {self.selected_domain}[/green]")
                    break
                else:
                    self.console.print("[red]Invalid selection. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a valid number.[/red]")

    def _simulate_agent_execution(self, agent_name: str, agent_input: Dict) -> Dict:
        """Execute actual agent instead of simulation"""
        try:
            # Prepare request based on agent type
            if agent_name == "Company Research Agent":
                company_name = agent_input.get("company_name", "")
                response = run_company_research_agent(company_name)
                
            elif agent_name == "Industry Analysis Agent":
                # Use company data from previous agent
                company_data = self._get_company_data_from_previous()
                if not company_data:
                    raise ValueError("Company data required from previous agent")
                response = run_industry_analysis_agent(company_data)
                
            elif agent_name == "Market Data Agent":
                # Use selected domain or from input
                domain = self.selected_domain or agent_input.get("domain", "")
                if not domain:
                    raise ValueError("Domain required for market data analysis")
                response = run_market_data_agent(domain)
                
            elif agent_name == "Competitive Landscape Agent":
                # Use selected domain and create opportunity structure
                if not self.selected_domain:
                    raise ValueError("Domain selection required from previous agent")
                
                # Create industry opportunity structure for competitive analysis
                industry_opportunity = {
                    "domain": self.selected_domain,
                    "score": 0.8,  # Default score
                    "rationale": f"Selected domain: {self.selected_domain}",
                    "sources": []
                }
                response = run_competitive_landscape_agent(industry_opportunity)
                
            elif agent_name == "Market Gap Analysis Agent":
                company_profile = self._get_company_data_from_previous()
                competitor_list = self._get_competitive_data_from_previous()
                market_stats = self._get_market_data_from_previous()
                
                if not all([company_profile, competitor_list, market_stats]):
                    raise ValueError("Missing required data from previous agents")
                
                combined_data = {
                    "company_profile": company_profile,
                    "competitor_list": competitor_list,
                    "market_stats": market_stats
                }
                response = run_market_gap_analysis_agent(combined_data)
                
            elif agent_name == "Opportunity Agent":
                gap_analysis = self._get_gap_analysis_from_previous()
                
                if not gap_analysis:
                    raise ValueError("Gap analysis data required from previous agent")
                
                response = run_opportunity_agent(gap_analysis)
                
            elif agent_name == "Report Synthesis Agent":
                # Collect all previous data
                combined_data = {
                    "company_research_data": self._get_company_data_from_previous(),
                    "domain_research_data": self._get_industry_data_from_previous(),
                    "market_research_data": self._get_market_data_from_previous(),
                    "competitive_research_data": self._get_competitive_data_from_previous(),
                    "gap_analysis_data": self._get_gap_analysis_from_previous(),
                    "opportunity_research_data": self._get_opportunity_data_from_previous()
                }
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

    def _get_company_data_from_previous(self):
        """Get company data from Company Research Agent output"""
        company_output = self.agent_outputs.get("Company Research Agent")
        if company_output and company_output.get("success") and company_output.get("data"):
            return company_output["data"]
        return None

    def _get_industry_data_from_previous(self):
        """Get industry data from Industry Analysis Agent output"""
        industry_output = self.agent_outputs.get("Industry Analysis Agent")
        if industry_output and industry_output.get("success") and industry_output.get("data"):
            return industry_output["data"]
        return None

    def _get_market_data_from_previous(self):
        """Get market data from Market Data Agent output"""
        market_output = self.agent_outputs.get("Market Data Agent")
        if market_output and market_output.get("success") and market_output.get("data"):
            return market_output["data"]
        return None

    def _get_competitive_data_from_previous(self):
        """Get competitive data from Competitive Landscape Agent output"""
        competitive_output = self.agent_outputs.get("Competitive Landscape Agent")
        if competitive_output and competitive_output.get("success") and competitive_output.get("data"):
            return competitive_output["data"]
        return None

    def _get_gap_analysis_from_previous(self):
        """Get gap analysis from Market Gap Analysis Agent output"""
        gap_output = self.agent_outputs.get("Market Gap Analysis Agent")
        if gap_output and gap_output.get("success") and gap_output.get("data"):
            return gap_output["data"]
        return None

    def _get_opportunity_data_from_previous(self):
        """Get opportunity data from Opportunity Agent output"""
        opportunity_output = self.agent_outputs.get("Opportunity Agent")
        if opportunity_output and opportunity_output.get("success") and opportunity_output.get("data"):
            return opportunity_output["data"]
        return None

    def _collect_agent_input(self, agent_name: str) -> Optional[Dict]:
        """Collect input for the agent based on actual requirements"""
        collected_input = {}
        
        # Handle different agent input requirements
        if agent_name == "Company Research Agent":
            company_name = Prompt.ask("Enter company name", default="")
            if company_name:
                collected_input["company_name"] = company_name
                
        elif agent_name == "Market Data Agent":
            # Check if we have selected domain from industry analysis
            if self.selected_domain:
                use_selected = Confirm.ask(f"Use selected domain '{self.selected_domain}'?", default=True)
                if use_selected:
                    collected_input["domain"] = self.selected_domain
                else:
                    domain = Prompt.ask("Enter market domain to analyze", default="")
                    if domain:
                        collected_input["domain"] = domain
            else:
                domain = Prompt.ask("Enter market domain to analyze", default="")
                if domain:
                    collected_input["domain"] = domain
                
        elif agent_name == "Competitive Landscape Agent":
            # Use selected domain or prompt
            if self.selected_domain:
                self.console.print(f"[green]Using selected domain: {self.selected_domain}[/green]")
                collected_input["auto_chain"] = True
            else:
                domain = Prompt.ask("Enter industry domain for competitive analysis", default="")
                if domain:
                    collected_input["domain"] = domain
                    
        # Other agents primarily use previous agent outputs
        elif agent_name in ["Industry Analysis Agent", "Market Gap Analysis Agent", 
                           "Opportunity Agent", "Report Synthesis Agent"]:
            # These agents get their data from previous agents automatically
            collected_input["auto_chain"] = True
        
        return collected_input if collected_input else {"auto_chain": True}

    def _validate_output(self, agent_name: str, output: Dict) -> Dict[str, Any]:
        """Validate agent output using proper validators"""
        try:
            # Check if it's a successful response first
            if not output.get("success", False):
                return {
                    "is_valid": False,
                    "issues": [f"Agent execution failed: {output.get('error', 'Unknown error')}"],
                    "schema_used": agent_name
                }
            
            # Check if data exists
            if "data" not in output or output["data"] is None:
                return {
                    "is_valid": False,
                    "issues": ["No data returned from agent"],
                    "schema_used": agent_name
                }
            
            # Use appropriate validator
            validator = self.validators.get(agent_name)
            if not validator:
                return {
                    "is_valid": False,
                    "issues": [f"No validator found for {agent_name}"],
                    "schema_used": agent_name
                }
            
            # Validate based on agent type
            if agent_name in ["Company Research Agent", "Market Data Agent"]:
                validation_result = validator.validate_output(output["data"])
            elif agent_name in ["Industry Analysis Agent", "Competitive Landscape Agent", 
                               "Market Gap Analysis Agent", "Opportunity Agent"]:
                validation_result = validator.validate_output(output["data"])
            elif agent_name == "Report Synthesis Agent":
                validation_result = validator.validate_output(output["data"])
            else:
                # Fallback validation
                validation_result = {"valid": True, "data": output["data"]}
            
            return {
                "is_valid": validation_result.get("valid", False),
                "issues": [validation_result.get("error", "Unknown validation error")] if not validation_result.get("valid", False) else [],
                "schema_used": agent_name
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "schema_used": agent_name
            }