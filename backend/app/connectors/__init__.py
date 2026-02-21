"""
Connector factory for creating data source connectors
"""
from .base import BaseConnector
from .postgresql import PostgreSQLConnector
from .mysql import MySQLConnector
from .mongodb import MongoDBConnector
from .rest_api import RestAPIConnector
from .csv_connector import CSVConnector


CONNECTOR_REGISTRY = {
    "postgresql": PostgreSQLConnector,
    "mysql": MySQLConnector,
    "mongodb": MongoDBConnector,
    "rest_api": RestAPIConnector,
    "csv": CSVConnector,
}


def create_connector(connector_type: str, config: dict, field_mapping: dict = None) -> BaseConnector:
    """Factory function to create connector instances"""
    connector_class = CONNECTOR_REGISTRY.get(connector_type.lower())
    if not connector_class:
        raise ValueError(f"Unknown connector type: {connector_type}")
    
    return connector_class(config, field_mapping)
