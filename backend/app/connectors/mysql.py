"""
MySQL connector implementation
"""
import pymysql
import pandas as pd
from typing import Dict, Any, Optional
from .base import BaseConnector


class MySQLConnector(BaseConnector):
    """MySQL database connector"""
    
    def connect(self) -> bool:
        """Establish MySQL connection"""
        try:
            self.connection = pymysql.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                database=self.config.get("database"),
                user=self.config.get("user"),
                password=self.config.get("password")
            )
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MySQL: {str(e)}")
    
    def disconnect(self) -> bool:
        """Close MySQL connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
        return True
    
    def test_connection(self) -> Dict[str, Any]:
        """Test MySQL connection"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()[0]
            cursor.close()
            self.disconnect()
            
            return {
                "status": "success",
                "message": "Connection successful",
                "version": version
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def fetch_data(self, query: Optional[str] = None, limit: Optional[int] = None) -> pd.DataFrame:
        """Fetch data from MySQL"""
        if not self.connection:
            self.connect()
        
        if not query:
            table = self.config.get("table", "transactions")
            query = f"SELECT * FROM {table}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        df = pd.read_sql_query(query, self.connection)
        return self.map_fields(df)
