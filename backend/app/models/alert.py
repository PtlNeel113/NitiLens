"""
Alert logging model for real-time notifications
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBSOCKET = "websocket"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Alert(Base):
    __tablename__ = "alerts_log"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.violation_id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False)
    
    channel = Column(SQLEnum(AlertChannel), nullable=False)
    recipient = Column(String(255))  # Email address, Slack channel, or user_id
    
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING)
    sent_at = Column(DateTime)
    error_message = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
