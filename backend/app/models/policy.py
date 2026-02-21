"""
Multi-policy support with versioning
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class PolicyStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    policy_name = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0")
    department = Column(String(100))
    regulatory_framework = Column(String(100))  # AML, GDPR, SOX, HIPAA, etc.
    
    # Language support
    original_language = Column(String(10), default="en")
    translated_text = Column(Text)
    translation_confidence = Column(Float)
    
    # File info
    file_path = Column(String(500))
    file_size = Column(String(50))
    
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.ACTIVE, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Metadata
    metadata = Column(JSON)
    
    # Relationships
    organization = relationship("Organization", back_populates="policies")
    rules = relationship("Rule", back_populates="policy", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="policy")
