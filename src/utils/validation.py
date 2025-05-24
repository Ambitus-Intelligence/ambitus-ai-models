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

class CompanyValidator:
    """Validator for Company Research Agent output"""
    
    def __init__(self):
        self.model = Company
        
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate company data against the Company schema.
        
        Args:
            data: Dictionary containing company information
            
        Returns:
            Dict with validation results
        """
        try:
            # Validate using Pydantic model
            validated_company = self.model.model_validate(data)
            
            return {
                "valid": True,
                "data": validated_company.model_dump(),
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
        Validate a JSON string containing company data.
        
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
        """Get the JSON schema for the Company model"""
        return self.model.model_json_schema()
