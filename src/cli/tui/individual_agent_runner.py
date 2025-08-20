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

from .keyboard_handler import KeyboardHandler, KeyCode, NavigationHandler, ContinuousInput

class IndividualAgentRunner:
    """Handles individual agent execution with two-panel layout"""
    
    def __init__(self, console: Console):
        self.console = console
        self.agents = self._get_agent_definitions()
        self.agent_navigator = NavigationHandler(list(self.agents.keys()))
        self.current_tab = "input"  # input, output, description
        self.tab_navigator = NavigationHandler(["input", "output", "description"])
        self.current_panel = "left"  # left, right
        self.agent_outputs = {}  # Store outputs for chaining
        self.keyboard = KeyboardHandler()
        self.input_fields = {}  # Store input field values
        
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
        """Main runner interface with continuous input and arrow key navigation"""
        with self.keyboard:
            while True:
                try:
                    self._show_interface()
                    
                    # Get key input
                    key = self.keyboard.get_key()
                    
                    if key.lower() == 'q' or key == KeyCode.ESC.value:
                        break
                    elif key == KeyCode.UP.value:
                        self._handle_up()
                    elif key == KeyCode.DOWN.value:
                        self._handle_down()
                    elif key == KeyCode.LEFT.value:
                        self._handle_left()
                    elif key == KeyCode.RIGHT.value:
                        self._handle_right()
                    elif key == KeyCode.TAB.value:
                        self._switch_panel()
                    elif key == KeyCode.ENTER.value:
                        self._handle_enter()
                    elif key.lower() == 'r':
                        self._run_current_agent()
                    elif key.lower() == 'c':
                        self._run_agent_chain()
                    elif key.lower() == 'i':
                        self._interactive_input()
                    elif key.lower() == 'x':
                        self._reset_outputs()
                        
                except KeyboardInterrupt:
                    break
    
    def _handle_up(self):
        """Handle up arrow key"""
        if self.current_panel == "left":
            self.agent_navigator.move_up()
        elif self.current_panel == "right" and self.current_tab == "input":
            # Navigate input fields
            pass
    
    def _handle_down(self):
        """Handle down arrow key"""
        if self.current_panel == "left":
            self.agent_navigator.move_down()
        elif self.current_panel == "right" and self.current_tab == "input":
            # Navigate input fields
            pass
    
    def _handle_left(self):
        """Handle left arrow key"""
        if self.current_panel == "right":
            self.tab_navigator.move_up()  # Move to previous tab
            self.current_tab = self.tab_navigator.get_selected_item()
    
    def _handle_right(self):
        """Handle right arrow key"""
        if self.current_panel == "right":
            self.tab_navigator.move_down()  # Move to next tab
            self.current_tab = self.tab_navigator.get_selected_item()
    
    def _handle_enter(self):
        """Handle enter key"""
        if self.current_panel == "left":
            # Select current agent and switch to right panel
            self.current_panel = "right"
        elif self.current_panel == "right":
            if self.current_tab == "input":
                self._interactive_input()
            else:
                self._run_current_agent()
    
    def _switch_panel(self):
        """Switch between left and right panels"""
        self.current_panel = "right" if self.current_panel == "left" else "left"
    
    def _interactive_input(self):
        """Interactive input for current agent"""
        current_agent_name = list(self.agents.keys())[self.agent_navigator.get_selected_index()]
        agent_def = self.agents[current_agent_name]
        
        self.console.print(f"\n[bold cyan]Interactive Input for {current_agent_name}[/bold cyan]")
        
        if current_agent_name not in self.input_fields:
            self.input_fields[current_agent_name] = {}
        
        for field, description in agent_def["input_schema"].items():
            current_value = self.input_fields[current_agent_name].get(field, "")
            
            # Use continuous input
            continuous_input = ContinuousInput(
                prompt=f"{field}: ",
                default=current_value,
                on_change=lambda value, f=field, a=current_agent_name: self._update_field(a, f, value)
            )
            
            new_value = continuous_input.run()
            self.input_fields[current_agent_name][field] = new_value
        
        self.console.print("\n[green]Input completed![/green]")
    
    def _update_field(self, agent_name: str, field: str, value: str):
        """Update field value in real-time"""
        if agent_name not in self.input_fields:
            self.input_fields[agent_name] = {}
        self.input_fields[agent_name][field] = value
    
    def _show_interface(self):
        """Display the two-panel interface with navigation indicators"""
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
        
        # Show navigation help
        help_text = Text()
        if self.current_panel == "left":
            help_text.append("[LEFT PANEL] ", style="bold green")
            help_text.append("↑↓: Navigate agents | Tab: Switch panels | Enter: Select | Q: Quit")
        else:
            help_text.append("[RIGHT PANEL] ", style="bold blue")
            help_text.append("←→: Switch tabs | Tab: Switch panels | Enter: Action | I: Interactive input")
        
        self.console.print(Panel(help_text, style="yellow"))
    
    def _create_agent_list_panel(self) -> Panel:
        """Create the left panel with agent selection"""
        agent_list = Table(show_header=False, box=None)
        agent_list.add_column("", style="cyan")
        
        for i, (agent_name, _) in enumerate(self.agents.items()):
            if i == self.agent_navigator.get_selected_index():
                if self.current_panel == "left":
                    agent_list.add_row(f"▶ {agent_name}", style="bold green")
                else:
                    agent_list.add_row(f"▷ {agent_name}", style="green")
            else:
                status = "✓" if agent_name in self.agent_outputs else "○"
                agent_list.add_row(f"{status} {agent_name}")
        
        controls = Text("\nControls:", style="bold")
        controls.append("\n[↑/↓] Navigate", style="dim")
        controls.append("\n[Tab] Switch Panel", style="dim")
        controls.append("\n[Enter] Select", style="dim")
        controls.append("\n[R] Run Agent", style="dim")
        controls.append("\n[C] Run Chain", style="dim")
        controls.append("\n[I] Interactive Input", style="dim")
        controls.append("\n[X] Reset", style="dim")
        controls.append("\n[Q] Quit", style="dim")
        
        content = Columns([agent_list, controls])
        
        panel_style = "bold blue" if self.current_panel == "left" else "blue"
        return Panel(content, title="Agent Selection", style=panel_style)
    
    def _create_tab_header(self) -> Panel:
        """Create tab header with navigation indicators"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for i, tab in enumerate(tab_names):
            if tab == self.current_tab:
                if self.current_panel == "right":
                    tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
                else:
                    tabs.append(f"[green]■ {tab.upper()}[/green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        panel_style = "bold yellow" if self.current_panel == "right" else "yellow"
        return Panel(" | ".join(tabs), style=panel_style)
    
    def _create_tab_content(self) -> Panel:
        """Create content for the current tab"""
        current_agent_name = list(self.agents.keys())[self.agent_navigator.get_selected_index()]
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
        """Create input form for the agent with current values"""
        form = Text("Input Requirements:\n\n", style="bold")
        
        # Check if we have previous agent output to use
        prev_agent_output = self._get_previous_agent_output(agent_name)
        current_values = self.input_fields.get(agent_name, {})
        
        for field, description in agent_def["input_schema"].items():
            form.append(f"{field}: ", style="cyan")
            form.append(f"{description}\n", style="dim")
            
            # Show current value if any
            current_value = current_values.get(field, "")
            if current_value:
                form.append(f"  Current: {current_value}\n", style="green")
            
            # Show if data is available from previous agent
            if prev_agent_output and field.lower() in [k.lower() for k in prev_agent_output.keys()]:
                form.append("  ✓ Available from previous agent\n", style="blue")
            else:
                form.append("  ⚠ Requires manual input\n", style="yellow")
            form.append("\n")
        
        form.append("\nPress [I] for Interactive Input", style="bold yellow")
        
        if prev_agent_output:
            form.append("\n\nPrevious Agent Output Available:", style="bold green")
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
            return Text("No output available yet.\nPress [R] to run agent or [Enter] to execute.", style="dim")
    
    def _run_current_agent(self):
        """Run the currently selected agent"""
        current_agent_name = list(self.agents.keys())[self.agent_navigator.get_selected_index()]
        
        # Get input from stored values or previous agent
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
        else:
            self.console.print("[yellow]No input available. Use [I] for interactive input.[/yellow]")
    
    def _collect_agent_input(self, agent_name: str) -> Optional[Dict]:
        """Collect input for the agent from stored values or previous agent"""
        agent_def = self.agents[agent_name]
        collected_input = {}
        
        # Try to use stored input values first
        stored_input = self.input_fields.get(agent_name, {})
        
        # Try to use previous agent output
        prev_output = self._get_previous_agent_output(agent_name)
        
        for field, description in agent_def["input_schema"].items():
            if field in stored_input and stored_input[field]:
                collected_input[field] = stored_input[field]
            elif prev_output and field.lower().replace('_', ' ') in ' '.join(prev_output.keys()).lower():
                collected_input[field] = prev_output
        
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
    
    def _run_agent_chain(self):
        """Run all agents in sequence"""
        self.console.print("[bold yellow]Running agent chain...[/bold yellow]")
        
        for i, agent_name in enumerate(self.agents.keys()):
            self.agent_navigator.set_selected_index(i)
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
    
    def _reset_outputs(self):
        """Reset all agent outputs and input fields"""
        self.agent_outputs.clear()
        self.input_fields.clear()
        self.console.print("[yellow]All outputs and inputs cleared[/yellow]")


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
