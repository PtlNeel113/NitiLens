"""
MongoDB connector implementation
"""
from pymongo import MongoClient
import pandas as pd
from typing import Dict, Any, Optional
from .base import BaseConnector


class MongoDBConnector(BaseConnector):
    """MongoDB database connector"""
    
    def connect(self) -> bool:
        """Establish MongoDB connection"""
        try:
            connection_string = self.config.get("connection_string")
            if not connection_string:
                host = self.config.get("host", "localhost")
                port = self.config.get("port", 27017)
                user = self.config.get("user")
                password = self.config.get("password")
                
                if user and password:
                    connection_string = f"mongodb://{user}:{password}@{host}:{port}"
                else:
                    connection_string = f"mongodb://{host}:{port}"
            
            self.connection = MongoClient(connection_string)
            # Test connection
            self.connection.server_info()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")
    
    def disconnect(self) -> bool:
        """Close MongoDB connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test MongoDB connection"""
        try:
            self.connect()
            info = self.connection.server_info()
            self.disconnect()
            
            return {
                "status": "success",
                "message": "Connection successful",
                "version": info.get("version")
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def fetch_data(self, query: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from MongoDB"""
        if not self.connection:
            self.connect()
        
        database = self.config.get("database")
        collection = self.config.get("collection", "transactions")
        
        db = self.connection[database]
        coll = db[collection]
        
        query_filter = query if query else {}
        cursor = coll.find(query_filter)
        
        if limit:
            cursor = cursor.limit(limit)
        
        data = list(cursor)
        df = pd.DataFrame(data)
        
        # Remove MongoDB _id if present
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)
        
        return self.map_fields(df)
