"""
Base connector class for all data source integrations
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd


class BaseConnector(ABC):
    """Abstract base class for all data connectors"""
    
    def __init__(self, config: Dict[str, Any], field_mapping: Optional[Dict[str, str]] = None):
        self.config = config
        self.field_mapping = field_mapping or {}
        self.connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close connection to data source"""
        pass
    
    @abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """Test connection and return status"""
        pass
    
    @abstractmethod
    def fetch_data(self, query: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from source"""
        pass
    
    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate data schema"""
        required_fields = ["transaction_id", "amount", "date"]
        missing_fields = [f for f in required_fields if f not in df.columns]
        
        return {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "available_fields": list(df.columns)
        }
    
    def map_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply field mapping to dataframe"""
        if not self.field_mapping:
            return df
        
        # Rename columns based on mapping
        return df.rename(columns=self.field_mapping)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata"""
        return {
            "type": self.__class__.__name__,
            "config": {k: v for k, v in self.config.items() if k not in ["password", "api_key"]},
            "field_mapping": self.field_mapping
        }
