from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ValidationError
import json

class Company(BaseModel):
    name: str
    industry: str
    description: str
    products: List[str]
    headquarters: str
    sources: List[str]

class IndustryOpportunity(BaseModel):
    domain: str
    score: float
    rationale: str
    sources: List[str]

class CompetitiveLandscape(BaseModel):
    competitor: str
    product: str
    market_share: float
    note: str
    sources: List[str]

class MarketData(BaseModel):
    market_size_usd: float
    CAGR: float
    key_drivers: List[str]
    sources: List[str]

class MarketGapAnalystInput(BaseModel):
    company_profile: Company
    competitor_list: List[CompetitiveLandscape]
    market_stats: MarketData

class MarketGapAnalystOutput(BaseModel):
    gap: str
    impact: str
    evidance: str
    sources: str


class BaseValidator:
    """Base validator class with common validation methods"""
    
    def __init__(self, model: BaseModel):
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

class CompanyValidator(BaseValidator):
    """Validator for Company Research Agent output"""
    
    def __init__(self):
        super().__init__(Company)

class IndustryAnalysisValidator:
    """Validator for Industry Analysis Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(Company)
        self.output_model = List[IndustryOpportunity]
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input company data"""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate industry analysis output against the expected schema.
        
        Args:
            data: List of industry opportunities
            
        Returns:
            Dict with validation results
        """
        try:
            validated_opportunities = [IndustryOpportunity.model_validate(item) for item in data]
            
            return {
                "valid": True,
                "data": [opp.model_dump() for opp in validated_opportunities],
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
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input Company model"""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output IndustryOpportunity list"""
        return {
            "type": "array",
            "items": IndustryOpportunity.model_json_schema()
        }

class CompetitiveLandscapeValidator:
    """Validator for Competitive Landscape Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(IndustryOpportunity)
        self.output_model = List[CompetitiveLandscape]
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input industry opportunity data"""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate competitive landscape output against the expected schema.
        
        Args:
            data: List of competitor information
            
        Returns:
            Dict with validation results
        """
        try:
            validated_competitors = [CompetitiveLandscape.model_validate(item) for item in data]
            
            return {
                "valid": True,
                "data": [comp.model_dump() for comp in validated_competitors],
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
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input IndustryOpportunity model"""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output CompetitiveLandscape list"""
        return {
            "type": "array",
            "items": CompetitiveLandscape.model_json_schema()
        }

class MarketGapAnalystValidator:
    """Validator for Market Gap Analyst Agent input and output"""
    
    def __init__(self):
        self.input_validator = BaseValidator(MarketGapAnalystInput)
        self.output_model = List[MarketGapAnalystOutput]
        
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate market gap analyst input model."""
        return self.input_validator.validate(data)
    
    def validate_output(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate market gap analysis output against the expected schema.
        
        Args:
            data: list of dict of general company stats.
            
        Returns:
            Dict with validation results
        """
        try:
            validated_market_gaps = [MarketGapAnalystOutput.model_validate(item) for item in data]
            
            return {
                "valid": True,
                "data": [i.model_dump() for i in validated_market_gaps],
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
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the input MarketGapAnalyst input model."""
        return self.input_validator.get_schema()
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for the output MarketGapAnalyst response list."""
        return {
            "type": "array",
            "items": MarketGapAnalystOutput.model_json_schema()
        }