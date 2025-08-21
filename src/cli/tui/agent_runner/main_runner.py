import json
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt, Confirm

from src.utils.models import (
    CompanyResearchRequest, MarketDataRequest, MarketGapAnalysisRequest,
    ReportSynthesisRequest, CompanyResponse, IndustryAnalysisResponse,
    MarketDataResponse, CompetitiveLandscapeResponse, MarketGapAnalysisResponse,
    OpportunityResponse, ReportSynthesisResponse
)

from src.utils.validation import (
    CompanyValidator, IndustryAnalysisValidator, MarketDataValidator,
    CompetitiveLandscapeValidator, MarketGapAnalysisValidator,
    OpportunityValidator, ReportSynthesisValidator
)

from .display_utils import AgentOutputStyler, TUIComponentBuilder
from .agent_executor import AgentExecutor
from .report_handler import ReportHandler
from .system_status import SystemStatusHandler
from ..environment_setup import EnvironmentSetupHandler


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
        self.output_lines_per_page = 18  # Reduced to make room for title
        
        # Initialize components
        self._initialize_validators()
        self.executor = AgentExecutor(console)
        self.styler = AgentOutputStyler()
        self.builder = TUIComponentBuilder()
        self.report_handler = ReportHandler(console)
        self.system_status = SystemStatusHandler(console)
        self.env_handler = EnvironmentSetupHandler(console)

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
    
    def run(self):
        """Main runner interface with two-panel layout"""
        # Clear console on entry
        #self.console.clear()
        
        while True:
            try:
                self._show_interface()
                choice = self._get_user_input()
                
                if choice == "quit":
                    # Clear console before exiting
                    #self.console.clear()
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
                elif choice == "reset_scroll":
                    self._reset_scroll()
                elif choice == "save_pdf":
                    self._save_pdf_report()
                elif choice == "mcp_toggle":
                    self._handle_mcp_toggle()
                elif choice == "api_key_setup":
                    self._handle_api_key_setup()
                    
            except KeyboardInterrupt:
                # Clear console on keyboard interrupt
                #self.console.clear()
                break
    
    def _get_user_input(self) -> str:
        """Get user input for navigation with updated controls"""
        key = self.console.input("")
        
        if key.lower() in ['q', 'quit']:
            return "quit"
        elif key.lower() in ['r', 'run']:
            return "run"
        elif key.lower() in ['c', 'chain']:
            return "chain"
        elif key.lower() == 'w':  # Navigate up in agent list
            return "prev"
        elif key.lower() == 's' and self._is_report_synthesis_agent():  # Save PDF for report agent
            return "save_pdf"
        elif key.lower() == 's':  # Navigate down in agent list
            return "next"
        elif key.lower() == 'a':  # Navigate left in tabs
            return "tab_prev"
        elif key.lower() == 'd':  # Navigate right in tabs
            return "tab_next"
        elif key.lower() == 'm':  # MCP Server management
            return "mcp_toggle"
        elif key.lower() == 'k':  # API Key management
            return "api_key_setup"
        elif key == '':  # Enter
            return "run"
        elif key.lower() == 'v':  # View full output
            return "view_full"
        elif key.lower() == 'u':  # Scroll up
            return "scroll_up"
        elif key.lower() == 'j':  # Scroll down
            return "scroll_down"
        elif key.lower() == 't':  # Reset scroll (T for Top)
            return "reset_scroll"
        else:
            return "invalid"
    
    def _is_report_synthesis_agent(self) -> bool:
        """Check if current agent is Report Synthesis Agent"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        return current_agent_name == "Report Synthesis Agent"
    
    def _get_available_tabs(self) -> List[str]:
        """Get available tabs based on current agent"""
        if self._is_report_synthesis_agent():
            return ["report", "description"]
        else:
            return ["input", "output", "description"]
    
    def _show_interface(self):
        """Display the two-panel interface"""
        #self.console.clear()
        
        layout = Layout()
        layout.split_column(
            Layout(self.builder.create_title_header(), size=4),
            Layout(name="main_content")
        )
        
        layout["main_content"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        # Left panel - Agent selection with system status
        layout["left"].update(self.builder.create_agent_list_panel(
            self.agents, self.current_agent_index, self.agent_outputs, self.system_status))
        
        # Right panel - Tabbed content
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        is_report_agent = self._is_report_synthesis_agent()
        has_scrollable_output = (
            (current_agent_name in self.agent_outputs and self.agent_outputs[current_agent_name].get("success")) or
            (is_report_agent and self.report_handler.can_generate_report(self.agent_outputs))
        )
        
        layout["right"].split_column(
            Layout(self.builder.create_tab_header(
                self.current_tab, has_scrollable_output, is_report_agent), size=3),
            Layout(self._create_tab_content())
        )
        
        self.console.print(layout)
    
    def _create_tab_content(self) -> Panel:
        """Create content for the current tab"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        agent_def = self.agents[current_agent_name]
        
        if self.current_tab == "description":
            content = Panel(agent_def["description"], title=f"{current_agent_name} - Description")
            return content
        
        elif self.current_tab == "report" and self._is_report_synthesis_agent():
            content = self._create_report_display()
            return Panel(content, title=f"{current_agent_name} - Report")
        
        elif self.current_tab == "input":
            prev_agent_output = self._get_previous_agent_output(current_agent_name)
            content = self.builder.create_input_form(current_agent_name, agent_def, prev_agent_output)
            return Panel(content, title=f"{current_agent_name} - Input")
        
        elif self.current_tab == "output":
            content = self._create_output_display(current_agent_name)
            return Panel(content, title=f"{current_agent_name} - Output")
        
        return Panel("Unknown tab", style="red")
    
    def _create_report_display(self) -> Text:
        """Create consolidated report display for Report Synthesis Agent"""
        content = Text()
        
        if not self.report_handler.can_generate_report(self.agent_outputs):
            content.append("❌ Cannot Generate Report\n\n", style="bold red")
            content.append("Missing data from required agents:\n", style="yellow")
            
            required_agents = [
                "Company Research Agent", "Industry Analysis Agent", "Market Data Agent",
                "Competitive Landscape Agent", "Market Gap Analysis Agent", "Opportunity Agent"
            ]
            
            for agent in required_agents:
                if agent not in self.agent_outputs or not self.agent_outputs[agent].get("success"):
                    content.append(f"  ❌ {agent}\n", style="red")
                else:
                    content.append(f"  ✅ {agent}\n", style="green")
            
            content.append("\nRun the missing agents to generate the report.", style="dim")
            return content
        
        # Generate consolidated report
        report_text = self.report_handler.create_consolidated_report_text(self.agent_outputs)
        
        # Handle scrolling for long reports
        report_lines = report_text.split('\n')
        total_lines = len(report_lines)
        
        # Ensure scroll offset is within bounds
        self.output_scroll_offset = max(0, min(self.output_scroll_offset, max(0, total_lines - self.output_lines_per_page)))
        
        if total_lines <= self.output_lines_per_page:
            # Show all content if it fits
            content.append(report_text, style="cyan")
            content.append(self.report_handler.get_pdf_save_instructions(self.agent_outputs), style="green")
        else:
            # Show paginated content
            start_line = self.output_scroll_offset
            end_line = min(start_line + self.output_lines_per_page, total_lines)
            
            visible_lines = report_lines[start_line:end_line]
            content.append('\n'.join(visible_lines), style="cyan")
            
            # Add scroll indicators
            current_page = (start_line // self.output_lines_per_page) + 1
            total_pages = max(1, (total_lines - 1) // self.output_lines_per_page + 1)
            
            content.append(f"\n\n--- Page {current_page}/{total_pages} (Lines {start_line + 1}-{end_line}/{total_lines}) ---", style="bold yellow")
            content.append("\n[U/J] Scroll  [T] Reset", style="dim")
            content.append(self.report_handler.get_pdf_save_instructions(self.agent_outputs), style="green")
        
        return content
    
    def _create_output_display(self, agent_name: str) -> Text:
        """Create styled output display for the agent with scrolling support"""
        if agent_name not in self.agent_outputs:
            return Text("No output available yet.\nRun the agent to generate output.\n\n[V] View Full Output (when available)", style="dim")
        
        output = self.agent_outputs[agent_name]
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
        styled_output = self.styler.create_styled_data_display(agent_name, output["data"])
        
        # Handle scrolling for long outputs
        output_lines = styled_output.split('\n')
        total_lines = len(output_lines)
        
        # Ensure scroll offset is within bounds
        self.output_scroll_offset = max(0, min(self.output_scroll_offset, max(0, total_lines - self.output_lines_per_page)))
        
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
            
            # Add scroll indicators with updated controls
            current_page = (start_line // self.output_lines_per_page) + 1
            total_pages = max(1, (total_lines - 1) // self.output_lines_per_page + 1)
            
            content.append(f"\n\n--- Page {current_page}/{total_pages} (Lines {start_line + 1}-{end_line}/{total_lines}) ---", style="bold yellow")
            content.append("\n[U/J] Scroll  [V] Raw JSON  [T] Reset", style="dim")
        
        return content
    
    def _scroll_output_up(self):
        """Scroll output up"""
        if self.current_tab == "output":
            self.output_scroll_offset = max(0, self.output_scroll_offset - 3)
    
    def _scroll_output_down(self):
        """Scroll output down"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                output = self.agent_outputs[current_agent_name]
                if output.get("success") and output.get("data"):
                    styled_output = self.styler.create_styled_data_display(current_agent_name, output["data"])
                    output_lines = styled_output.split('\n')
                    total_lines = len(output_lines)
                    max_offset = max(0, total_lines - self.output_lines_per_page)
                    self.output_scroll_offset = min(max_offset, self.output_scroll_offset + 3)

    def _reset_scroll(self):
        """Reset scroll to top"""
        self.output_scroll_offset = 0
    
    def _show_full_output(self):
        """Show full JSON output in a separate view"""
        if self.current_tab == "output":
            current_agent_name = list(self.agents.keys())[self.current_agent_index]
            if current_agent_name in self.agent_outputs:
                output = self.agent_outputs[current_agent_name]
                self.builder.show_full_output_view(self.console, current_agent_name, output)
                self.output_scroll_offset = 0  # Reset scroll when returning
    
    def _move_to_next_agent(self):
        """Move to the next agent in the list"""
        if self.current_agent_index < len(self.agents) - 1:
            self.current_agent_index += 1
            # Reset to appropriate tab when switching agents
            self.current_tab = "report" if self._is_report_synthesis_agent() else "input"
            self.output_scroll_offset = 0
    
    def _move_to_previous_agent(self):
        """Move to the previous agent in the list"""
        if self.current_agent_index > 0:
            self.current_agent_index -= 1
            # Reset to appropriate tab when switching agents
            self.current_tab = "report" if self._is_report_synthesis_agent() else "input"
            self.output_scroll_offset = 0
    
    def _switch_tab_next(self):
        """Switch to the next tab"""
        tabs = self._get_available_tabs()
        current_index = tabs.index(self.current_tab) if self.current_tab in tabs else 0
        self.current_tab = tabs[(current_index + 1) % len(tabs)]
    
    def _switch_tab_prev(self):
        """Switch to the previous tab"""
        tabs = self._get_available_tabs()
        current_index = tabs.index(self.current_tab) if self.current_tab in tabs else 0
        self.current_tab = tabs[(current_index - 1) % len(tabs)]
    
    def _run_current_agent(self):
        """Run the currently selected agent"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        
        agent_input = self.executor.collect_agent_input(current_agent_name, self.agent_outputs, self.selected_domain)
        
        if agent_input:
            output = self.executor.execute_agent(current_agent_name, agent_input, self.selected_domain)
            
            validation_result = self._validate_output(current_agent_name, output)
            
            if validation_result["is_valid"]:
                self.agent_outputs[current_agent_name] = output
                self.console.print(f"[green]✓ {current_agent_name} completed successfully![/green]")
                
                # Handle domain selection after Industry Analysis
                if current_agent_name == "Industry Analysis Agent" and output.get("success"):
                    selected = self.executor.handle_domain_selection(output.get("data", []))
                    if selected:
                        self.selected_domain = selected
            else:
                self.console.print(f"[red]✗ {current_agent_name} output validation failed![/red]")
                self.console.print(f"[yellow]Issues: {', '.join(validation_result['issues'])}[/yellow]")
            
            input("Press Enter to continue...")
    
    def _run_agent_chain(self):
        """Run all agents in sequence"""
        self.console.print("[yellow]Running full agent chain...[/yellow]")
        
        for i, agent_name in enumerate(self.agents.keys()):
            self.current_agent_index = i
            self.console.print(f"[blue]Running {agent_name}...[/blue]")
            
            if agent_name == "Company Research Agent":
                company_name = Prompt.ask("Enter company name for chain execution")
                agent_input = {"company_name": company_name}
            else:
                agent_input = self.executor.collect_agent_input(agent_name, self.agent_outputs, self.selected_domain)
            
            if agent_input:
                output = self.executor.execute_agent(agent_name, agent_input, self.selected_domain)
                validation_result = self._validate_output(agent_name, output)
                
                if validation_result["is_valid"]:
                    self.agent_outputs[agent_name] = output
                    self.console.print(f"[green]✓ {agent_name} completed successfully[/green]")
                    
                    if agent_name == "Industry Analysis Agent" and output.get("success"):
                        selected = self.executor.handle_domain_selection(output.get("data", []))
                        if selected:
                            self.selected_domain = selected
                else:
                    self.console.print(f"[red]✗ {agent_name} failed: {', '.join(validation_result['issues'])}[/red]")
                    break
        
        input("Press Enter to continue...")
    
    def _reset_outputs(self):
        """Reset all agent outputs"""
        self.agent_outputs.clear()
        self.selected_domain = None
        self.output_scroll_offset = 0
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
            data = previous_output.get("data")
            
            # Handle different data types from previous agents
            if isinstance(data, list):
                # For list data (like from Industry Analysis), create a summary dict
                return {
                    "opportunities": data,
                    "selected_domain": self.selected_domain,
                    "count": len(data)
                }
            elif isinstance(data, dict):
                # For dict data, return as-is
                return data
            else:
                # For other types, wrap in a dict
                return {"data": data}
        
        return None
    
    def _validate_output(self, agent_name: str, output: Dict) -> Dict[str, Any]:
        """Validate agent output using proper validators"""
        try:
            if not output.get("success", False):
                return {
                    "is_valid": False,
                    "issues": [f"Agent execution failed: {output.get('error', 'Unknown error')}"],
                    "schema_used": agent_name
                }
            
            if "data" not in output or output["data"] is None:
                return {
                    "is_valid": False,
                    "issues": ["No data returned from agent"],
                    "schema_used": agent_name
                }
            
            validator = self.validators.get(agent_name)
            if not validator:
                return {
                    "is_valid": False,
                    "issues": [f"No validator found for {agent_name}"],
                    "schema_used": agent_name
                }
            
            validation_result = validator.validate_output(output["data"])
            
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
    
    def _save_pdf_report(self):
        """Handle PDF report saving"""
        if not self._is_report_synthesis_agent():
            return
        
        self.console.print("[yellow]Generating PDF report...[/yellow]")
        result = self.report_handler.save_pdf_report(self.agent_outputs)
        
        if result["success"]:
            file_size_mb = result["file_size"] / (1024 * 1024)
            self.console.print(f"[green]✓ PDF report saved successfully![/green]")
            self.console.print(f"[cyan]Location: {result['file_path']}[/cyan]")
            self.console.print(f"[cyan]Size: {file_size_mb:.2f} MB[/cyan]")
        else:
            self.console.print(f"[red]✗ Failed to save PDF: {result['error']}[/red]")
        
        input("Press Enter to continue...")
    
    def _create_tab_content(self) -> Panel:
        """Create content for the current tab"""
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        agent_def = self.agents[current_agent_name]
        
        if self.current_tab == "description":
            content = Panel(agent_def["description"], title=f"{current_agent_name} - Description")
            return content
        
        elif self.current_tab == "report" and self._is_report_synthesis_agent():
            content = self._create_report_display()
            return Panel(content, title=f"{current_agent_name} - Report")
        
        elif self.current_tab == "input":
            prev_agent_output = self._get_previous_agent_output(current_agent_name)
            content = self.builder.create_input_form(current_agent_name, agent_def, prev_agent_output)
            return Panel(content, title=f"{current_agent_name} - Input")
        
        elif self.current_tab == "output":
            content = self._create_output_display(current_agent_name)
            return Panel(content, title=f"{current_agent_name} - Output")
        
        return Panel("Unknown tab", style="red")
    
    def _create_report_display(self) -> Text:
        """Create consolidated report display for Report Synthesis Agent"""
        content = Text()
        
        if not self.report_handler.can_generate_report(self.agent_outputs):
            content.append("❌ Cannot Generate Report\n\n", style="bold red")
            content.append("Missing data from required agents:\n", style="yellow")
            
            required_agents = [
                "Company Research Agent", "Industry Analysis Agent", "Market Data Agent",
                "Competitive Landscape Agent", "Market Gap Analysis Agent", "Opportunity Agent"
            ]
            
            for agent in required_agents:
                if agent not in self.agent_outputs or not self.agent_outputs[agent].get("success"):
                    content.append(f"  ❌ {agent}\n", style="red")
                else:
                    content.append(f"  ✅ {agent}\n", style="green")
            
            content.append("\nRun the missing agents to generate the report.", style="dim")
            return content
        
        # Generate consolidated report
        report_text = self.report_handler.create_consolidated_report_text(self.agent_outputs)
        
        # Handle scrolling for long reports
        report_lines = report_text.split('\n')
        total_lines = len(report_lines)
        
        # Ensure scroll offset is within bounds
        self.output_scroll_offset = max(0, min(self.output_scroll_offset, max(0, total_lines - self.output_lines_per_page)))
        
        if total_lines <= self.output_lines_per_page:
            # Show all content if it fits
            content.append(report_text, style="cyan")
            content.append(self.report_handler.get_pdf_save_instructions(self.agent_outputs), style="green")
        else:
            # Show paginated content
            start_line = self.output_scroll_offset
            end_line = min(start_line + self.output_lines_per_page, total_lines)
            
            visible_lines = report_lines[start_line:end_line]
            content.append('\n'.join(visible_lines), style="cyan")
            
            # Add scroll indicators
            current_page = (start_line // self.output_lines_per_page) + 1
            total_pages = max(1, (total_lines - 1) // self.output_lines_per_page + 1)
            
            content.append(f"\n\n--- Page {current_page}/{total_pages} (Lines {start_line + 1}-{end_line}/{total_lines}) ---", style="bold yellow")
            content.append("\n[U/J] Scroll  [T] Reset", style="dim")
            content.append(self.report_handler.get_pdf_save_instructions(self.agent_outputs), style="green")
        
        return content
    
    def _show_interface(self):
        """Display the two-panel interface"""
        #self.console.clear()
        
        layout = Layout()
        layout.split_column(
            Layout(self.builder.create_title_header(), size=4),
            Layout(name="main_content")
        )
        
        layout["main_content"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=2)
        )
        
        # Left panel - Agent selection with system status
        layout["left"].update(self.builder.create_agent_list_panel(
            self.agents, self.current_agent_index, self.agent_outputs, self.system_status))
        
        # Right panel - Tabbed content
        current_agent_name = list(self.agents.keys())[self.current_agent_index]
        is_report_agent = self._is_report_synthesis_agent()
        has_scrollable_output = (
            (current_agent_name in self.agent_outputs and self.agent_outputs[current_agent_name].get("success")) or
            (is_report_agent and self.report_handler.can_generate_report(self.agent_outputs))
        )
        
        layout["right"].split_column(
            Layout(self.builder.create_tab_header(
                self.current_tab, has_scrollable_output, is_report_agent), size=3),
            Layout(self._create_tab_content())
        )
        
        self.console.print(layout)
    
    def _move_to_next_agent(self):
        """Move to the next agent in the list"""
        if self.current_agent_index < len(self.agents) - 1:
            self.current_agent_index += 1
            # Reset to appropriate tab when switching agents
            self.current_tab = "report" if self._is_report_synthesis_agent() else "input"
            self.output_scroll_offset = 0
    
    def _move_to_previous_agent(self):
        """Move to the previous agent in the list"""
        if self.current_agent_index > 0:
            self.current_agent_index -= 1
            # Reset to appropriate tab when switching agents
            self.current_tab = "report" if self._is_report_synthesis_agent() else "input"
            self.output_scroll_offset = 0
    
    def _handle_mcp_toggle(self):
        """Handle MCP server start/stop"""
        status = self.system_status.check_mcp_server_status()
        
        if status["running"]:
            # Server is running, offer to stop
            if Confirm.ask("[yellow]MCP Server is running. Stop it?[/yellow]", default=False):
                result = self.system_status.stop_mcp_server()
                if result["success"]:
                    self.console.print(f"[green]✓ {result['message']}[/green]")
                else:
                    self.console.print(f"[red]✗ {result['message']}[/red]")
        else:
            # Server is not running, offer to start
            if Confirm.ask("[yellow]MCP Server is not running. Start it?[/yellow]", default=True):
                result = self.system_status.start_mcp_server()
                if result["success"]:
                    self.console.print(f"[green]✓ {result['message']}[/green]")
                else:
                    self.console.print(f"[red]✗ {result['message']}[/red]")
        
        input("Press Enter to continue...")
    
    def _handle_api_key_setup(self):
        """Handle API key setup"""
        self.env_handler.show_environment_setup()