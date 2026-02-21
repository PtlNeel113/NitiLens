"""
CSV file connector implementation
"""
import pandas as pd
from typing import Dict, Any, Optional
from .base import BaseConnector


class CSVConnector(BaseConnector):
    """CSV file connector"""
    
    def connect(self) -> bool:
        """Validate CSV file path"""
        if "file_path" not in self.config:
            raise ValueError("file_path is required for CSV connector")
        return True
    
    def disconnect(self) -> bool:
        """No persistent connection for CSV"""
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test CSV file access"""
        try:
            file_path = self.config.get("file_path")
            df = pd.read_csv(file_path, nrows=5)
            
            return {
                "status": "success",
                "message": f"CSV file accessible with {len(df.columns)} columns",
                "columns": list(df.columns)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def fetch_data(self, query: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from CSV file"""
        file_path = self.config.get("file_path")
        
        kwargs = {}
        if limit:
            kwargs["nrows"] = limit
        
        df = pd.read_csv(file_path, **kwargs)
        return self.map_fields(df)
