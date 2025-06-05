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
