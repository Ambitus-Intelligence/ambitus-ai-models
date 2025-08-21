import os
from typing import Dict, Any, Optional
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt
from pathlib import Path
from datetime import datetime

from src.agents.report_synthesis_agent import create_pdf_stream


class ReportHandler:
    """Handles report synthesis and PDF generation"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def can_generate_report(self, agent_outputs: Dict[str, Any]) -> bool:
        """Check if all required agent outputs are available for report generation"""
        required_agents = [
            "Company Research Agent",
            "Industry Analysis Agent", 
            "Market Data Agent",
            "Competitive Landscape Agent",
            "Market Gap Analysis Agent",
            "Opportunity Agent"
        ]
        
        for agent in required_agents:
            if agent not in agent_outputs:
                return False
            if not agent_outputs[agent].get("success") or not agent_outputs[agent].get("data"):
                return False
        
        return True
    
    def create_consolidated_report_text(self, agent_outputs: Dict[str, Any]) -> str:
        """Create formatted text report from all agent outputs"""
        if not self.can_generate_report(agent_outputs):
            return "❌ Cannot generate report: Missing required agent data\n\nRequired agents:\n- Company Research Agent\n- Industry Analysis Agent\n- Market Data Agent\n- Competitive Landscape Agent\n- Market Gap Analysis Agent\n- Opportunity Agent"
        
        # Get company name for title
        company_name = agent_outputs.get("Company Research Agent", {}).get("data", {}).get("name", "Unknown Company")
        
        report = f"📋 COMPREHENSIVE MARKET RESEARCH REPORT\n"
        report += f"{'='*60}\n\n"
        report += f"Company: {company_name}\n"
        report += f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"
        
        # Company Overview
        company_data = agent_outputs["Company Research Agent"]["data"]
        report += "🏢 COMPANY OVERVIEW\n"
        report += f"{'-'*30}\n"
        report += f"Industry: {company_data.get('industry', 'N/A')}\n"
        report += f"Headquarters: {company_data.get('headquarters', 'N/A')}\n"
        report += f"Description: {company_data.get('description', 'N/A')}\n\n"
        
        # Products & Services
        products = company_data.get('products', [])
        if products:
            report += f"Products & Services ({len(products)}):\n"
            for i, product in enumerate(products, 1):
                report += f"  {i}. {product}\n"
        report += "\n"
        
        # Industry Analysis Summary
        industry_data = agent_outputs["Industry Analysis Agent"]["data"]
        if industry_data:
            report += "🎯 INDUSTRY OPPORTUNITIES\n"
            report += f"{'-'*30}\n"
            top_opportunities = sorted(industry_data, key=lambda x: x.get('score', 0), reverse=True)[:3]
            for i, opp in enumerate(top_opportunities, 1):
                score = opp.get('score', 0)
                report += f"{i}. {opp.get('domain', 'Unknown')} (Score: {score:.2f})\n"
                report += f"   {opp.get('rationale', 'No rationale')}\n\n"
        
        # Market Statistics
        market_data = agent_outputs["Market Data Agent"]["data"]
        report += "📊 MARKET STATISTICS\n"
        report += f"{'-'*30}\n"
        market_size = market_data.get('market_size_usd', 0)
        if market_size >= 1_000_000_000:
            size_display = f"${market_size/1_000_000_000:.1f}B USD"
        elif market_size >= 1_000_000:
            size_display = f"${market_size/1_000_000:.1f}M USD"
        else:
            size_display = f"${market_size:,.0f} USD"
        
        cagr = market_data.get('CAGR', 0)
        cagr_percent = cagr * 100 if cagr < 1 else cagr
        
        report += f"Market Size: {size_display}\n"
        report += f"Growth Rate (CAGR): {cagr_percent:.1f}%\n\n"
        
        # Key Market Drivers
        drivers = market_data.get('key_drivers', [])
        if drivers:
            report += "Key Market Drivers:\n"
            for i, driver in enumerate(drivers, 1):
                report += f"  {i}. {driver}\n"
        report += "\n"
        
        # Competitive Landscape Summary
        competitive_data = agent_outputs["Competitive Landscape Agent"]["data"]
        if competitive_data:
            report += "🏆 TOP COMPETITORS\n"
            report += f"{'-'*30}\n"
            top_competitors = sorted(competitive_data, key=lambda x: x.get('market_share', 0), reverse=True)[:5]
            for i, comp in enumerate(top_competitors, 1):
                market_share = comp.get('market_share', 0)
                report += f"{i}. {comp.get('competitor', 'Unknown')} - {market_share:.1%} market share\n"
                report += f"   Product: {comp.get('product', 'N/A')}\n"
                report += f"   Position: {comp.get('note', 'N/A')}\n\n"
        
        # Market Gaps Summary
        gap_data = agent_outputs["Market Gap Analysis Agent"]["data"]
        if gap_data:
            high_impact_gaps = [gap for gap in gap_data if gap.get('impact', '').lower() == 'high']
            if high_impact_gaps:
                report += "🔍 HIGH IMPACT MARKET GAPS\n"
                report += f"{'-'*30}\n"
                for i, gap in enumerate(high_impact_gaps, 1):
                    report += f"{i}. {gap.get('gap', 'Unknown gap')}\n"
                    report += f"   Evidence: {gap.get('evidence', 'No evidence')}\n\n"
        
        # Strategic Opportunities Summary  
        opportunity_data = agent_outputs["Opportunity Agent"]["data"]
        if opportunity_data:
            high_priority_opps = [opp for opp in opportunity_data if opp.get('priority', '').lower() == 'high']
            if high_priority_opps:
                report += "💰 HIGH PRIORITY OPPORTUNITIES\n"
                report += f"{'-'*30}\n"
                for i, opp in enumerate(high_priority_opps, 1):
                    report += f"{i}. {opp.get('title', 'Unknown opportunity')}\n"
                    report += f"   Description: {opp.get('description', 'No description')}\n\n"
        
        report += f"\n{'='*60}\n"
        report += "Report generated by Ambitus Intelligence\n"
        
        return report
    
    def save_pdf_report(self, agent_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and save PDF report"""
        try:
            if not self.can_generate_report(agent_outputs):
                return {
                    "success": False,
                    "error": "Cannot generate PDF: Missing required agent data"
                }
            
            # Get save location from user
            default_filename = f"market_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Ask for save location
            save_path = Prompt.ask(
                f"Enter file path to save PDF report",
                default=str(Path.home() / "Downloads" / default_filename)
            )
            
            # Ensure .pdf extension
            if not save_path.lower().endswith('.pdf'):
                save_path += '.pdf'
            
            # Create directory if it doesn't exist
            save_dir = Path(save_path).parent
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for PDF generation
            combined_data = {
                "company_research_data": agent_outputs["Company Research Agent"]["data"],
                "domain_research_data": agent_outputs["Industry Analysis Agent"]["data"],
                "market_research_data": agent_outputs["Market Data Agent"]["data"],
                "competitive_research_data": agent_outputs["Competitive Landscape Agent"]["data"],
                "gap_analysis_data": agent_outputs["Market Gap Analysis Agent"]["data"],
                "opportunity_research_data": agent_outputs["Opportunity Agent"]["data"]
            }
            
            # Generate PDF
            pdf_bytes = create_pdf_stream(combined_data)
            
            # Write to file
            with open(save_path, 'wb') as f:
                f.write(pdf_bytes)
            
            return {
                "success": True,
                "file_path": save_path,
                "file_size": len(pdf_bytes)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save PDF: {str(e)}"
            }
    
    def get_pdf_save_instructions(self, agent_outputs: Dict[str, Any]) -> str:
        """Get instructions for PDF saving based on current state"""
        if self.can_generate_report(agent_outputs):
            return "\n💾 [S] Save PDF Report - Generate and save comprehensive PDF report"
        else:
            missing_agents = []
            required_agents = [
                "Company Research Agent", "Industry Analysis Agent", "Market Data Agent",
                "Competitive Landscape Agent", "Market Gap Analysis Agent", "Opportunity Agent"
            ]
            
            for agent in required_agents:
                if agent not in agent_outputs or not agent_outputs[agent].get("success"):
                    missing_agents.append(agent)
            
            return f"\n❌ PDF Save Unavailable - Missing data from: {', '.join(missing_agents)}"
