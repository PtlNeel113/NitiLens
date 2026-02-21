"""
Data connector model for ERP/CRM integrations
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class ConnectorType(str, enum.Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REST_API = "rest_api"
    CSV = "csv"


class ConnectorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class Connector(Base):
    __tablename__ = "connectors"

    connector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    connector_name = Column(String(255), nullable=False)
    connector_type = Column(SQLEnum(ConnectorType), nullable=False)
    
    # Encrypted connection details
    connection_config = Column(JSON)  # Encrypted credentials
    field_mapping = Column(JSON)  # Maps source fields to compliance fields
    
    status = Column(SQLEnum(ConnectorStatus), default=ConnectorStatus.INACTIVE)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="connectors")
