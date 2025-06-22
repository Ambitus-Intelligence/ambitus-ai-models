from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel, ValidationError
import json

from src.utils.models import (
    Company, IndustryOpportunity, CompetitiveLandscape, 
    MarketData, MarketGap, Opportunity, MarketDataRequest, 
    MarketGapAnalysisRequest
)


class BaseValidator:
    """Base validator class with common validation methods"""
    
    def __init__(self, model: Type[BaseModel]):
        self.model = model
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against the model schema.
        
        Args:
            data: Dictionary containing data to validate
            
        Returns:
            Dict with validation results
        """
        try:
            validated_data = self.model.model_validate(data)
            
            return {
                "valid": True,
                "data": validated_data.model_dump(),
                "error": None
            }
            
        except ValidationError as e:
            return {
                "valid": False,
                "data": None,
                "error": str(e),
                "error_details": e.errors()
            }
        except Exception as e:
            return {
                "valid": False,
                "data": None,
                "error": f"Unexpected validation error: {str(e)}"
            }
    
    def validate_json_string(self, json_string: str) -> Dict[str, Any]:
        """
        Validate a JSON string.
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            Dict with validation results
        """
        try:
            data = json.loads(json_string)
            return self.validate(data)
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "data": None,
                "error": f"Invalid JSON format: {str(e)}"
            }
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the model"""
        return self.model.model_json_schema()


class ListValidator:
    """Base validator for list-based outputs"""
    
    def __init__(self, item_model: Type[BaseModel]):
        self.item_model = item_model
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate list output against the expected schema.
        
        Args:
            data: List of items to validate
            
        Returns:
            Dict with validation results
        """
        try:
            if not isinstance(data, list):
                return {
                    "valid": False,
                    "data": None,
                    "error": f"Expected list but got {type(data).__name__}"
                }
                
            validated_items = [self.item_model.model_validate(item) for item in data]
            
            return {
                "valid": True,
                "data": [item.model_dump() for item in validated_items],
                "error": None
            }
            
        except ValidationError as e:
            return {
                "valid": False,
                "data": None,
                "error": str(e),
                "error_details": e.errors()
            }
        except Exception as e:
            return {
                "valid": False,
                "data": None,
                "error": f"Unexpected validation error: {str(e)}"
            }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output list"""
        return {
            "type": "array",
            "items": self.item_model.model_json_schema()
        }


class CompanyValidator(BaseValidator):
    """Validator for Company Research Agent output"""
    
    def __init__(self):
        super().__init__(Company)


class IndustryAnalysisValidator:
    """Validator for Industry Analysis Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(Company)
        self.output_validator = ListValidator(IndustryOpportunity)
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input company data"""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate industry analysis output"""
        return self.output_validator.validate_output(data)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input Company model"""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output IndustryOpportunity list"""
        return self.output_validator.get_output_schema()


class CompetitiveLandscapeValidator:
    """Validator for Competitive Landscape Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(IndustryOpportunity)
        self.output_validator = ListValidator(CompetitiveLandscape)
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input industry opportunity data"""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate competitive landscape output"""
        return self.output_validator.validate_output(data)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input IndustryOpportunity model"""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output CompetitiveLandscape list"""
        return self.output_validator.get_output_schema()


class MarketGapAnalysisValidator:
    """Validator for Market Gap Analysis Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(MarketGapAnalysisRequest)
        self.output_validator = ListValidator(MarketGap)
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate market gap analysis input model."""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate market gap analysis output"""
        return self.output_validator.validate_output(data)
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input MarketGapAnalysis input model."""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output MarketGap response list."""
        return self.output_validator.get_output_schema()


class MarketDataValidator:
    """Validator for Market Data Agent input and output."""

    def __init__(self):
        self.input_validator = BaseValidator(MarketDataRequest)
        self.output_validator = BaseValidator(MarketData)

    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Market Data Agent input (domain string wrapped in dict)."""
        return self.input_validator.validate(data)

    def validate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Market Data Agent output (market data dictionary)."""
        return self.output_validator.validate(data)

    def get_input_schema(self) -> Dict[str, Any]:
        """Return input schema for market data."""
        return MarketDataRequest.model_json_schema()

    def get_output_schema(self) -> Dict[str, Any]:
        """Return output schema for market data."""
        return MarketData.model_json_schema()


class OpportunityValidator:
    """Validator for Opportunity Agent input and output"""

    def __init__(self):
        self.input_validator = ListValidator(MarketGap)
        self.output_validator = ListValidator(Opportunity)

    def validate_input(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate input for Opportunity Agent (list of market gaps)"""
        return self.input_validator.validate_output(data)

    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate the Opportunity Agent output"""
        return self.output_validator.validate_output(data)

    def get_input_schema(self) -> Dict[str, Any]:
        return self.input_validator.get_output_schema()

    def get_output_schema(self) -> Dict[str, Any]:
        return self.output_validator.get_output_schema()


class ReportSynthesisValidator:
    """
    PLACEHOLDER: Validator for Report Synthesis Agent
    
    TODO: Implement comprehensive validation in issue #47
    """
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder input validation for report synthesis
        """
        try:
            # Basic validation - at least one data section should be present
            required_sections = [
                "company_profile", "industry_analysis", "market_data",
                "competitive_landscape", "market_gaps", "opportunities"
            ]
            
            has_data = any(section in data and data[section] is not None 
                          for section in required_sections)
            
            if not has_data:
                return {
                    "valid": False,
                    "error": "At least one data section must be provided"
                }
            
            return {
                "valid": True,
                "data": data
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Input validation error: {str(e)}"
            }
    
    def validate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder output validation for report synthesis
        """
        try:
            required_fields = ["pdf_content", "report_title", "generated_at"]
            
            for field in required_fields:
                if field not in data:
                    return {
                        "valid": False,
                        "error": f"Missing required field: {field}"
                    }
            
            return {
                "valid": True,
                "data": data
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Output validation error: {str(e)}"
            }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return the input schema for report synthesis"""
        return {
            "type": "object",
            "properties": {
                "company_profile": {"type": "object"},
                "industry_analysis": {"type": "array"},
                "market_data": {"type": "object"},
                "competitive_landscape": {"type": "array"},
                "market_gaps": {"type": "array"},
                "opportunities": {"type": "array"}
            },
            "description": "Combined outputs from all previous agents for report synthesis"
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Return the output schema for report synthesis"""
        return {
            "type": "object",
            "properties": {
                "pdf_content": {"type": "string", "format": "binary"},
                "report_title": {"type": "string"},
                "generated_at": {"type": "string", "format": "date-time"},
                "placeholder": {"type": "boolean"}
            },
            "required": ["pdf_content", "report_title", "generated_at"]
        }