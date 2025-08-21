import json
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax

class IndividualAgentRunner:
    """Handles individual agent execution with two-panel layout"""
    
    def __init__(self, console: Console):
        self.console = console
        self.agents = self._get_agent_definitions()
        self.current_agent_index = 0
        self.current_tab = "input"  # input, output, description
        self.agent_outputs = {}  # Store outputs for chaining
        
    def _get_agent_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Define all available agents with their specifications"""
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
- Company name or domain
- Research scope (basic/detailed)
- Specific focus areas (optional)

**Output Format:**
- Structured company profile
- Business strategy analysis
- Technical infrastructure overview
- Recent developments and news
""",
                "input_schema": {
                    "company_name": "Company name or domain to research",
                    "research_scope": "Research depth (basic/detailed)",
                    "focus_areas": "Specific areas to focus on (optional)"
                },
                "next_agent": "Industry Analysis Agent"
            },
            "Industry Analysis Agent": {
                "description": """
## Industry Analysis Agent

**Purpose:** Analyze industry trends and identify expansion domains.

**Key Functions:**
- Industry landscape mapping
- Market trend analysis
- Regulatory environment assessment
- Technology adoption patterns
- Growth opportunity identification

**Input Requirements:**
- Industry/sector information
- Company context from previous agent
- Geographic scope
- Time horizon for analysis

**Output Format:**
- Industry overview and trends
- Market size and growth projections
- Competitive dynamics
- Regulatory landscape
- Technology disruptions
""",
                "input_schema": {
                    "industry_sector": "Primary industry or sector",
                    "geographic_scope": "Geographic regions to analyze",
                    "time_horizon": "Analysis timeframe (1-5 years)",
                    "company_context": "Context from Company Research Agent"
                },
                "next_agent": "Market Data Agent"
            },
            "Market Data Agent": {
                "description": """
## Market Data Agent

**Purpose:** Fetch quantitative market metrics and data.

**Key Functions:**
- Market size and valuation data
- Growth rate calculations
- Customer segment analysis
- Revenue projections
- Investment flow tracking

**Input Requirements:**
- Market segments to analyze
- Geographic regions
- Data timeframe
- Metric types needed

**Output Format:**
- Quantitative market metrics
- Historical and projected data
- Market size breakdowns
- Growth rate analysis
- Investment trends
""",
                "input_schema": {
                    "market_segments": "Specific market segments to analyze",
                    "geographic_regions": "Target geographic markets",
                    "data_timeframe": "Historical and projection period",
                    "metric_types": "Types of metrics needed"
                },
                "next_agent": "Competitive Landscape Agent"
            },
            "Competitive Landscape Agent": {
                "description": """
## Competitive Landscape Agent

**Purpose:** Map competitors and their market offerings.

**Key Functions:**
- Competitor identification and profiling
- Product/service comparison
- Market positioning analysis
- Competitive advantages assessment
- Threat level evaluation

**Input Requirements:**
- Industry context
- Company positioning
- Geographic scope
- Competitive analysis depth

**Output Format:**
- Competitor profiles and analysis
- Market positioning map
- Competitive advantages/disadvantages
- Threat assessment matrix
- Strategic recommendations
""",
                "input_schema": {
                    "industry_context": "Industry context from previous analysis",
                    "company_positioning": "Current company market position",
                    "analysis_depth": "Level of competitive analysis needed",
                    "focus_competitors": "Specific competitors to focus on (optional)"
                },
                "next_agent": "Market Gap Analysis Agent"
            },
            "Market Gap Analysis Agent": {
                "description": """
## Market Gap Analysis Agent

**Purpose:** Detect unmet market needs and opportunities.

**Key Functions:**
- Gap identification in current market
- Unmet customer needs analysis
- Technology opportunity assessment
- Market inefficiency detection
- Innovation opportunity mapping

**Input Requirements:**
- Market data and competitive landscape
- Customer pain points
- Technology trends
- Business model innovations

**Output Format:**
- Identified market gaps
- Opportunity sizing and prioritization
- Customer need analysis
- Technology opportunity assessment
- Innovation recommendations
""",
                "input_schema": {
                    "market_data": "Market data from previous analysis",
                    "competitive_landscape": "Competitive analysis results",
                    "customer_segments": "Target customer segments",
                    "technology_trends": "Relevant technology trends"
                },
                "next_agent": "Opportunity Agent"
            },
            "Opportunity Agent": {
                "description": """
## Opportunity Agent

**Purpose:** Generate specific growth opportunities and strategies.

**Key Functions:**
- Business opportunity generation
- Strategic initiative development
- Growth pathway identification
- Risk-reward analysis
- Implementation roadmap creation

**Input Requirements:**
- Market gaps and opportunities
- Company capabilities
- Resource constraints
- Strategic objectives

**Output Format:**
- Prioritized opportunity list
- Strategic recommendations
- Implementation roadmaps
- Resource requirements
- Risk assessments
""",
                "input_schema": {
                    "market_gaps": "Identified market gaps and opportunities",
                    "company_capabilities": "Current company strengths/capabilities",
                    "resource_constraints": "Available resources and limitations",
                    "strategic_objectives": "Company strategic goals"
                },
                "next_agent": "Report Synthesis Agent"
            },
            "Report Synthesis Agent": {
                "description": """
## Report Synthesis Agent

**Purpose:** Compile comprehensive final research report.

**Key Functions:**
- Data synthesis and integration
- Executive summary creation
- Strategic recommendation prioritization
- Report formatting and presentation
- Key insights highlighting

**Input Requirements:**
- All previous agent outputs
- Report format preferences
- Audience specifications
- Key focus areas

**Output Format:**
- Executive summary
- Detailed findings report
- Strategic recommendations
- Implementation timeline
- Appendices with supporting data
""",
                "input_schema": {
                    "previous_outputs": "All previous agent analysis results",
                    "report_format": "Preferred report format and structure",
                    "target_audience": "Primary audience for the report",
                    "key_priorities": "Key priorities to highlight"
                },
                "next_agent": None
            }
        }
    
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
                    
            except KeyboardInterrupt:
                break
    
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
        
        return Panel(" | ".join(tabs), style="yellow")
    
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
        """Create output display for the agent"""
        if agent_name in self.agent_outputs:
            output = self.agent_outputs[agent_name]
            
            # Validate output first
            validation_result = self._validate_output(agent_name, output)
            
            content = Text("Output Status:\n", style="bold")
            
            if validation_result["is_valid"]:
                content.append("✓ Valid Output\n\n", style="green")
            else:
                content.append("✗ Output Validation Failed\n", style="red")
                content.append(f"Issues: {', '.join(validation_result['issues'])}\n\n", style="yellow")
            
            content.append("Output Data:\n", style="bold")
            
            # Pretty print JSON output
            output_json = json.dumps(output, indent=2)
            if len(output_json) > 500:
                content.append(f"{output_json[:500]}...\n[truncated]", style="cyan")
            else:
                content.append(output_json, style="cyan")
            
            return content
        else:
            return Text("No output available yet.\nRun the agent to generate output.", style="dim")
    
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
    
    def _collect_agent_input(self, agent_name: str) -> Optional[Dict]:
        """Collect input for the agent"""
        agent_def = self.agents[agent_name]
        collected_input = {}
        
        # Try to use previous agent output first
        prev_output = self._get_previous_agent_output(agent_name)
        
        for field, description in agent_def["input_schema"].items():
            # Check if we can use previous agent output
            if prev_output and field.lower().replace('_', ' ') in ' '.join(prev_output.keys()).lower():
                collected_input[field] = prev_output
            else:
                # Manual input
                value = Prompt.ask(f"Enter {field}", default="")
                if value:
                    collected_input[field] = value
        
        return collected_input if collected_input else None
    
    def _get_previous_agent_output(self, current_agent: str) -> Optional[Dict]:
        """Get output from the previous agent in the chain"""
        agent_names = list(self.agents.keys())
        current_index = agent_names.index(current_agent)
        
        if current_index > 0:
            prev_agent = agent_names[current_index - 1]
            return self.agent_outputs.get(prev_agent)
        
        return None
    
    def _simulate_agent_execution(self, agent_name: str, agent_input: Dict) -> Dict:
        """Simulate agent execution (replace with actual agent implementation)"""
        # This is a placeholder - replace with actual agent execution logic
        return {
            "agent_name": agent_name,
            "input_received": agent_input,
            "execution_status": "completed",
            "results": f"Simulated results for {agent_name}",
            "timestamp": "2024-01-01T00:00:00Z",
            "confidence_score": 0.85,
            "data_sources": ["source1", "source2"],
            "recommendations": [f"Recommendation 1 from {agent_name}", f"Recommendation 2 from {agent_name}"]
        }
    
    def _validate_output(self, agent_name: str, output: Dict) -> Dict[str, Any]:
        """Validate agent output using validation model"""
        validator = OutputValidator()
        return validator.validate(agent_name, output)
    
    def _move_to_next_agent(self):
        """Move to next agent in the list"""
        if self.current_agent_index < len(self.agents) - 1:
            self.current_agent_index += 1
    
    def _move_to_previous_agent(self):
        """Move to previous agent in the list"""
        if self.current_agent_index > 0:
            self.current_agent_index -= 1
    
    def _switch_tab_next(self):
        """Switch to next tab"""
        tabs = ["input", "output", "description"]
        current_index = tabs.index(self.current_tab)
        self.current_tab = tabs[(current_index + 1) % len(tabs)]
    
    def _switch_tab_prev(self):
        """Switch to previous tab"""
        tabs = ["input", "output", "description"]
        current_index = tabs.index(self.current_tab)
        self.current_tab = tabs[(current_index - 1) % len(tabs)]
    
    def _switch_tab(self):
        """Switch between tabs (kept for backward compatibility)"""
        self._switch_tab_next()

    def _run_agent_chain(self):
        """Run all agents in sequence"""
        self.console.print("[bold yellow]Running agent chain...[/bold yellow]")
        
        for i, agent_name in enumerate(self.agents.keys()):
            self.current_agent_index = i
            self.console.print(f"[cyan]Running {agent_name}...[/cyan]")
            
            # Collect input
            agent_input = self._collect_agent_input(agent_name)
            if not agent_input:
                self.console.print(f"[red]Failed to collect input for {agent_name}[/red]")
                break
            
            # Execute agent
            output = self._simulate_agent_execution(agent_name, agent_input)
            
            # Validate output
            validation_result = self._validate_output(agent_name, output)
            
            if validation_result["is_valid"]:
                self.agent_outputs[agent_name] = output
                self.console.print(f"[green]✓ {agent_name} completed[/green]")
            else:
                self.console.print(f"[red]✗ {agent_name} validation failed[/red]")
                break
        
        self.console.print("[bold green]Agent chain completed![/bold green]")
        input("Press Enter to continue...")
    
    def _reset_outputs(self):
        """Reset all agent outputs"""
        if Confirm.ask("Reset all agent outputs?"):
            self.agent_outputs.clear()
            self.console.print("[yellow]All outputs cleared[/yellow]")


class OutputValidator:
    """Validates agent outputs using predefined schemas"""
    
    def __init__(self):
        self.validation_schemas = {
            "Company Research Agent": {
                "required_fields": ["agent_name", "results", "execution_status"],
                "result_types": ["business_strategy", "technical_strategy", "market_position"],
                "min_confidence": 0.7
            },
            "Industry Analysis Agent": {
                "required_fields": ["agent_name", "results", "execution_status"],
                "result_types": ["industry_trends", "market_size", "growth_projections"],
                "min_confidence": 0.6
            },
            "Market Data Agent": {
                "required_fields": ["agent_name", "results", "data_sources"],
                "result_types": ["quantitative_metrics", "market_data"],
                "min_confidence": 0.8
            },
            "Competitive Landscape Agent": {
                "required_fields": ["agent_name", "results", "recommendations"],
                "result_types": ["competitor_analysis", "market_positioning"],
                "min_confidence": 0.7
            },
            "Market Gap Analysis Agent": {
                "required_fields": ["agent_name", "results", "recommendations"],
                "result_types": ["gap_analysis", "opportunities"],
                "min_confidence": 0.6
            },
            "Opportunity Agent": {
                "required_fields": ["agent_name", "results", "recommendations"],
                "result_types": ["growth_opportunities", "strategic_initiatives"],
                "min_confidence": 0.7
            },
            "Report Synthesis Agent": {
                "required_fields": ["agent_name", "results", "execution_status"],
                "result_types": ["executive_summary", "final_report"],
                "min_confidence": 0.8
            }
        }
    
    def validate(self, agent_name: str, output: Dict) -> Dict[str, Any]:
        """Validate agent output against schema"""
        if agent_name not in self.validation_schemas:
            return {"is_valid": True, "issues": []}
        
        schema = self.validation_schemas[agent_name]
        issues = []
        
        # Check required fields
        for field in schema["required_fields"]:
            if field not in output:
                issues.append(f"Missing required field: {field}")
        
        # Check confidence score
        if "confidence_score" in output:
            if output["confidence_score"] < schema["min_confidence"]:
                issues.append(f"Confidence score too low: {output['confidence_score']}")
        else:
            issues.append("Missing confidence score")
        
        # Check execution status
        if output.get("execution_status") != "completed":
            issues.append("Agent execution not completed successfully")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "schema_used": agent_name
        }