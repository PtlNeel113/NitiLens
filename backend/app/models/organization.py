"""
Multi-tenant organization model
"""
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class SubscriptionPlan(str, enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_name = Column(String(255), nullable=False, unique=True)
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.BASIC)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Subscription limits
    policy_limit = Column(String(50), default="1")  # "1", "10", "unlimited"
    transaction_limit = Column(String(50), default="10000")  # "10000", "1000000", "unlimited"
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="organization", cascade="all, delete-orphan")
    connectors = relationship("Connector", back_populates="organization", cascade="all, delete-orphan")
