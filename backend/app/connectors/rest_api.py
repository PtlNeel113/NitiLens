"""
REST API connector implementation
"""
import httpx
import pandas as pd
from typing import Dict, Any, Optional
from .base import BaseConnector


class RestAPIConnector(BaseConnector):
    """REST API connector"""
    
    def connect(self) -> bool:
        """Validate API configuration"""
        required = ["base_url"]
        missing = [k for k in required if k not in self.config]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        return True
    
    def disconnect(self) -> bool:
        """No persistent connection for REST API"""
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test REST API connection"""
        try:
            base_url = self.config.get("base_url")
            headers = self.config.get("headers", {})
            
            # Add API key if provided
            api_key = self.config.get("api_key")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = httpx.get(f"{base_url}/health", headers=headers, timeout=10)
            
            return {
                "status": "success" if response.status_code == 200 else "error",
                "message": f"Status code: {response.status_code}",
                "response": response.text[:200]
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def fetch_data(self, query: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from REST API"""
        base_url = self.config.get("base_url")
        endpoint = self.config.get("endpoint", "/data")
        headers = self.config.get("headers", {})
        
        # Add API key if provided
        api_key = self.config.get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        params = {}
        if limit:
            params["limit"] = limit
        if query:
            params["query"] = query
        
        response = httpx.get(f"{base_url}{endpoint}", headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and "data" in data:
            df = pd.DataFrame(data["data"])
        else:
            df = pd.DataFrame([data])
        
        return self.map_fields(df)
