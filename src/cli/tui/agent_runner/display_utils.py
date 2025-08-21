import json
from typing import Dict, List, Any
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.align import Align


class AgentOutputStyler:
    """Utility class for styling agent outputs"""
    
    @staticmethod
    def style_company_data(data: Dict) -> str:
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
    
    @staticmethod
    def style_industry_data(data: List[Dict]) -> str:
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
    
    @staticmethod
    def style_market_data(data: Dict) -> str:
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
    
    @staticmethod
    def style_competitive_data(data: List[Dict]) -> str:
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
    
    @staticmethod
    def style_gap_analysis_data(data: List[Dict]) -> str:
        """Style market gap analysis data"""
        output = f"🔍 MARKET GAP ANALYSIS\n{'='*50}\n\n"
        
        if not data:
            return output + "No market gaps identified."
        
        # Ensure data is a list
        if not isinstance(data, list):
            return output + f"Invalid data format: expected list, got {type(data).__name__}"
        
        # Group by impact level
        high_impact = [gap for gap in data if gap.get('impact', '').lower() == 'high']
        medium_impact = [gap for gap in data if gap.get('impact', '').lower() == 'medium']
        low_impact = [gap for gap in data if gap.get('impact', '').lower() == 'low']
        other_impact = [gap for gap in data if gap.get('impact', '').lower() not in ['high', 'medium', 'low']]
        
        for impact_level, gaps, emoji in [
            ('HIGH IMPACT', high_impact, '🔥'),
            ('MEDIUM IMPACT', medium_impact, '⚡'),
            ('LOW IMPACT', low_impact, '💡'),
            ('OTHER', other_impact, '📍')
        ]:
            if gaps:
                output += f"{emoji} {impact_level} GAPS ({len(gaps)})\n{'-'*40}\n"
                for i, gap in enumerate(gaps, 1):
                    output += f"\n{i}. {gap.get('gap', 'Unknown gap')}\n"
                    output += f"   Impact: {gap.get('impact', 'Not specified')}\n"
                    output += f"   Evidence: {gap.get('evidence', 'No evidence provided')}\n"
                    source = gap.get('source', 'No source')
                    output += f"   Source: {source}\n"
                output += "\n"
        
        return output
    
    @staticmethod
    def style_opportunity_data(data: List[Dict]) -> str:
        """Style opportunity data"""
        output = f"💰 BUSINESS OPPORTUNITIES\n{'='*50}\n\n"
        
        if not data:
            return output + "No opportunities identified."
        
        # Ensure data is a list
        if not isinstance(data, list):
            return output + f"Invalid data format: expected list, got {type(data).__name__}"
        
        # Group by priority
        high_priority = [opp for opp in data if opp.get('priority', '').lower() == 'high']
        medium_priority = [opp for opp in data if opp.get('priority', '').lower() == 'medium']
        low_priority = [opp for opp in data if opp.get('priority', '').lower() == 'low']
        other_priority = [opp for opp in data if opp.get('priority', '').lower() not in ['high', 'medium', 'low']]
        
        for priority_level, opps, emoji in [
            ('HIGH PRIORITY', high_priority, '🚀'),
            ('MEDIUM PRIORITY', medium_priority, '⭐'),
            ('LOW PRIORITY', low_priority, '💼'),
            ('OTHER', other_priority, '📋')
        ]:
            if opps:
                output += f"{emoji} {priority_level} OPPORTUNITIES ({len(opps)})\n{'-'*45}\n"
                for i, opp in enumerate(opps, 1):
                    output += f"\n{i}. {opp.get('title', 'Unknown opportunity')}\n"
                    output += f"   Priority: {opp.get('priority', 'Not specified')}\n"
                    output += f"   Description: {opp.get('description', 'No description provided')}\n"
                    sources = opp.get('sources', [])
                    if sources and isinstance(sources, list):
                        output += f"   Sources: {', '.join(sources[:3])}"
                        if len(sources) > 3:
                            output += f" (+{len(sources)-3} more)"
                        output += "\n"
                    elif sources:
                        output += f"   Sources: {str(sources)}\n"
                output += "\n"
        
        return output
    
    @staticmethod
    def style_report_data(data: Dict) -> str:
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
    
    @staticmethod
    def create_styled_data_display(agent_name: str, data: Any) -> str:
        """Create stylized display for agent data based on agent type"""
        try:
            if agent_name == "Company Research Agent":
                return AgentOutputStyler.style_company_data(data)
            elif agent_name == "Industry Analysis Agent":
                return AgentOutputStyler.style_industry_data(data)
            elif agent_name == "Market Data Agent":
                return AgentOutputStyler.style_market_data(data)
            elif agent_name == "Competitive Landscape Agent":
                return AgentOutputStyler.style_competitive_data(data)
            elif agent_name == "Market Gap Analysis Agent":
                return AgentOutputStyler.style_gap_analysis_data(data)
            elif agent_name == "Opportunity Agent":
                return AgentOutputStyler.style_opportunity_data(data)
            elif agent_name == "Report Synthesis Agent":
                return AgentOutputStyler.style_report_data(data)
            else:
                return json.dumps(data, indent=2)
        except Exception as e:
            return f"Error displaying data: {str(e)}\n\nRaw data:\n{json.dumps(data, indent=2)}"


class TUIComponentBuilder:
    """Builder for TUI components"""
    
    @staticmethod
    def create_agent_list_panel(agents: Dict, current_index: int, agent_outputs: Dict, system_status_handler=None) -> Panel:
        """Create the left panel with agent selection and system status"""
        # Agent list table
        agent_list = Table(show_header=False, box=None, padding=(0, 1))
        agent_list.add_column("", style="cyan", no_wrap=True)
        
        for i, (agent_name, _) in enumerate(agents.items()):
            # Truncate long agent names for display
            display_name = agent_name.replace(" Agent", "")
            if len(display_name) > 20:
                display_name = display_name[:17] + "..."
                
            if i == current_index:
                agent_list.add_row(f"▶ {display_name}", style="bold green")
            else:
                status = "✓" if agent_name in agent_outputs else "○"
                agent_list.add_row(f"{status} {display_name}")
        
        # Controls section
        controls = Text()
        controls.append("Controls:\n", style="bold")
        controls.append("[W/S] Navigate\n", style="dim")
        controls.append("[A/D] Tabs\n", style="dim")
        controls.append("[R] Run Agent\n", style="dim")
        controls.append("[C] Run Chain\n", style="dim")
        controls.append("[M] MCP Server\n", style="dim")
        controls.append("[K] API Key\n", style="dim")
        controls.append("[Q] Quit", style="dim")
        
        # System status section
        status_text = Text()
        status_text.append("System Status:\n", style="bold")
        
        if system_status_handler:
            # Get current status
            mcp_status = system_status_handler.check_mcp_server_status()
            api_status = system_status_handler.check_openai_key_status()
            
            # MCP Server status
            status_text.append("MCP: ", style="bold")
            if mcp_status["running"]:
                status_text.append("✅ Running\n", style="green")
            else:
                status_text.append("❌ Stopped\n", style="red")
            
            # API Key status
            status_text.append("API: ", style="bold")
            if api_status["available"]:
                status_text.append("✅ Set\n", style="green")
            else:
                status_text.append("❌ Missing\n", style="red")
            
            status_text.append("\n[M] Toggle MCP\n[K] Set API Key", style="yellow")
        else:
            status_text.append("Status unavailable", style="red")
        
        # Create a layout for better organization
        from rich.layout import Layout as InnerLayout
        content_layout = InnerLayout()
        content_layout.split_column(
            InnerLayout(agent_list, name="agents", size=8),
            InnerLayout(controls, name="controls", size=9),
            InnerLayout(status_text, name="status")
        )
        
        return Panel(content_layout, title="Agent Selection", style="blue")
    
    @staticmethod
    def create_title_header() -> Panel:
        """Create the title header for the agent runner"""
        from rich.align import Align
        
        # Create title text
        title_text = Text()
        title_text.append("Ambitus", style="bold blue")
        title_text.append(" Agent Runner", style="italic cyan")
        
        # Create subtitle text
        subtitle_text = Text("Market Research Automation Platform", style="dim")
        
        # Create combined content
        content = Text()
        content.append(title_text)
        content.append("\n")
        content.append(subtitle_text)
        
        # Center align the entire content
        centered_content = Align.center(content)
        
        return Panel(centered_content, style="blue", padding=(0, 1))

    @staticmethod
    def create_tab_header(current_tab: str, has_scrollable_output: bool = False, is_report_agent: bool = False) -> Panel:
        """Create tab header with different tabs for report agent"""
        tabs = []
        
        if is_report_agent:
            tab_names = ["report", "description"]
        else:
            tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output/report tabs
        if current_tab in ["output", "report"] and has_scrollable_output:
            if is_report_agent and current_tab == "report":
                tabs.append("[dim]| [U/J] Scroll [S] Save PDF [T] Reset[/dim]")
            else:
                tabs.append("[dim]| [U/J] Scroll [V] Full View [T] Reset[/dim]")
        
        return Panel(" ".join(tabs), style="yellow")
    
    @staticmethod
    def create_input_form(agent_name: str, agent_def: Dict, prev_agent_output: Dict = None) -> Text:
        """Create input form for the agent"""
        form = Text("Input Requirements:\n\n", style="bold")
        
        for field, description in agent_def["input_schema"].items():
            form.append(f"{field}: ", style="cyan")
            form.append(f"{description}\n", style="dim")
            
            # Show if data is available from previous agent
            if prev_agent_output:
                # Handle different field checking for different data types
                if field.lower() == "domain" and "selected_domain" in prev_agent_output:
                    form.append("  ✓ Domain selected from Industry Analysis\n", style="green")
                elif field.lower() in [k.lower() for k in prev_agent_output.keys()]:
                    form.append("  ✓ Available from previous agent\n", style="green")
                elif field.lower() == "company_data" and any(key in prev_agent_output for key in ["name", "industry", "description"]):
                    form.append("  ✓ Available from previous agent\n", style="green")
                else:
                    form.append("  ⚠ Requires manual input\n", style="yellow")
            else:
                form.append("  ⚠ Requires manual input\n", style="yellow")
            form.append("\n")
        
        if prev_agent_output:
            form.append("\nPrevious Agent Output Available:", style="bold green")
            
            # Show relevant information based on data type
            if "selected_domain" in prev_agent_output:
                form.append(f"\nSelected Domain: {prev_agent_output['selected_domain']}", style="dim")
                if "opportunities" in prev_agent_output:
                    form.append(f"\nOpportunities Found: {prev_agent_output.get('count', 0)}", style="dim")
            else:
                # Show truncated JSON for other data types
                preview = json.dumps(prev_agent_output, indent=2)[:200]
                form.append(f"\n{preview}...", style="dim")
        
        return form
    
    @staticmethod
    def show_full_output_view(console, agent_name: str, output: Dict):
        """Show full JSON output in a separate view"""
        #console.clear()
        console.print(f"\n[bold blue]Full Output - {agent_name}[/bold blue]")
        console.print("=" * 60)
        
        # Show raw JSON with syntax highlighting
        json_content = json.dumps(output, indent=2)
        syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        console.print("\n[dim]Press Enter to return to main view...[/dim]")
        input()
        # Clear console before returning to main view
        #console.clear()
