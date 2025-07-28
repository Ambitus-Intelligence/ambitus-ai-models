import os
import json
import traceback
from typing import Dict, Any
from datetime import datetime
from io import BytesIO
import weasyprint
from jinja2 import Template


def create_pdf_stream(input_data: Dict[str,Any]) -> bytes:
    """
    Stream PDF report by taking all agent output inputs
    
    Args:
        input_data(dict): all agent outputs combined.
    
    Returns:
        pdf_bytes(bytes) : streamed PDF response.
    
    """
    # Read the HTML template
    with open('src/utils/report_template.html', 'r', encoding='utf-8') as file:
        template_content = file.read()
    
    # Jinja2 template for input_data injection
    template = Template(template_content)

    # Timestmps
    now = datetime.now()
    generation_data = {
        'generation_date': now.strftime('%B %d, %Y'),
        'generation_time': now.strftime('%I:%M %p'),
        **input_data
    }

    # HTML report
    html_output = template.render(**generation_data)

    # Convert HTML report to Weasyprint HTML doc
    weasy_html = weasyprint.HTML(string=html_output)

    # PDF stream with A4 opti. and custom meta-data 
    pdf_bytes = weasy_html.write_pdf(
        stylesheets=None,
        optimize_images=True,
        font_size=16,
        presentational_hints=True,
        pdf_identifier=None,
        pdf_version='1.7',
        pdf_forms=False,
        pdf_metadata={
            'title': f"Company Research Report - {input_data.get('company_research_data', {}).get('name', 'Unknown Company')}",
            'author': 'Ambitus Intelligence',
            'subject': f"Business Research Analysis for {input_data.get('company_research_data', {}).get('name', 'Unknown Company')}",
            'creator': 'Ambitus Intelligence Research Platform',
            'producer': 'Ambitus Intelligence',
            'keywords': f"{input_data.get('company_research_data', {}).get('industry', '')}, market research, competitive analysis"
        }
    )
    return pdf_bytes

def run_report_synthesis_agent(input_data: Dict[str,Any]) -> Dict[str,Any]:
    """
    Run the report synthesis agent for a combined all-agent input.

    Args:
        input_data(dict): Combined ouput of all the agents following upto this one.
    
    Returns:
        final_response(dict): Dict containing success status and PDF data or error details
    """
    try:
        # Extract company name for report title
        company_name = "Unknown Company"
        if "company_research_data" in input_data:
            company_name = input_data["company_research_data"].get("name", company_name)
        
        # Generate PDF
        pdf_data = create_pdf_stream(input_data)
        
        return {
            "success": True,
            "data": {
                "pdf_content": pdf_data,
                "report_title": f"Market Research Report: {company_name}",
                "generated_at": datetime.now().isoformat(),
                "placeholder": True
            },
            "raw_response": "Research Synthesis Report PDF successfully generated !"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"implementation error: {str(e)}",
            "traceback": traceback.format_exc(),
            "raw_response": None
        }
