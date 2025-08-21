import json
from typing import Dict, List, Any
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax


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
    
    @staticmethod
    def style_opportunity_data(data: List[Dict]) -> str:
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
    def create_agent_list_panel(agents: Dict, current_index: int, agent_outputs: Dict) -> Panel:
        """Create the left panel with agent selection"""
        agent_list = Table(show_header=False, box=None)
        agent_list.add_column("", style="cyan")
        
        for i, (agent_name, _) in enumerate(agents.items()):
            if i == current_index:
                agent_list.add_row(f"▶ {agent_name}", style="bold green")
            else:
                status = "✓" if agent_name in agent_outputs else "○"
                agent_list.add_row(f"{status} {agent_name}")
        
        controls = Text("\nControls:", style="bold")
        controls.append("\n[W/S] Navigate Agents", style="dim")
        controls.append("\n[A/D] Navigate Tabs", style="dim")
        controls.append("\n[Enter/R] Run Agent", style="dim")
        controls.append("\n[C] Run Chain", style="dim")
        controls.append("\n[Q] Quit", style="dim")
        
        content = Columns([agent_list, controls])
        return Panel(content, title="Agent Selection", style="blue")
    
    @staticmethod
    def create_tab_header(current_tab: str, has_scrollable_output: bool = False) -> Panel:
        """Create tab header"""
        tabs = []
        tab_names = ["input", "output", "description"]
        
        for tab in tab_names:
            if tab == current_tab:
                tabs.append(f"[bold green]■ {tab.upper()}[/bold green]")
            else:
                tabs.append(f"[dim]□ {tab.upper()}[/dim]")
        
        # Add scroll info for output tab
        if current_tab == "output" and has_scrollable_output:
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
            if prev_agent_output and field.lower() in [k.lower() for k in prev_agent_output.keys()]:
                form.append("  ✓ Available from previous agent\n", style="green")
            else:
                form.append("  ⚠ Requires manual input\n", style="yellow")
            form.append("\n")
        
        if prev_agent_output:
            form.append("\nPrevious Agent Output Available:", style="bold green")
            form.append(f"\n{json.dumps(prev_agent_output, indent=2)[:200]}...", style="dim")
        
        return form
    
    @staticmethod
    def show_full_output_view(console, agent_name: str, output: Dict):
        """Show full JSON output in a separate view"""
        console.clear()
        console.print(f"\n[bold blue]Full Output - {agent_name}[/bold blue]")
        console.print("=" * 60)
        
        # Show raw JSON with syntax highlighting
        json_content = json.dumps(output, indent=2)
        syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
        console.print(syntax)
        
        console.print("\n[dim]Press Enter to return to main view...[/dim]")
        input()
