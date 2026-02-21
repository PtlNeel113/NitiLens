"""
User model with RBAC
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
