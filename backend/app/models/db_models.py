"""
SQLAlchemy database models for multi-tenant enterprise platform
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Float, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


# Enums
class PolicyStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class RuleStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class ViolationStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    COMPLIANCE_ADMIN = "compliance_admin"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class SubscriptionPlan(str, enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


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


class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    SLACK = "slack"
    WEBSOCKET = "websocket"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


# Models
class Organization(Base):
    __tablename__ = "organizations"

    org_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_name = Column(String(255), nullable=False, unique=True)
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.BASIC)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    policy_limit = Column(String(50), default="1")
    transaction_limit = Column(String(50), default="10000")
    
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="organization", cascade="all, delete-orphan")
    connectors = relationship("Connector", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    organization = relationship("Organization", back_populates="users")


class Policy(Base):
    __tablename__ = "policies"

    policy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    policy_name = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0")
    department = Column(String(100), index=True)
    regulatory_framework = Column(String(100), index=True)
    
    original_language = Column(String(10), default="en")
    translated_text = Column(Text)
    translation_confidence = Column(Float)
    
    file_path = Column(String(500))
    file_size = Column(String(50))
    
    status = Column(SQLEnum(PolicyStatus), default=PolicyStatus.ACTIVE, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    metadata = Column(JSON)
    
    organization = relationship("Organization", back_populates="policies")
    rules = relationship("Rule", back_populates="policy", cascade="all, delete-orphan")
    violations = relationship("Violation", back_populates="policy")


class Rule(Base):
    __tablename__ = "rules"

    rule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.policy_id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Versioning for policy change impact
    previous_rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.rule_id"))
    is_active = Column(Boolean, default=True, index=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    
    rule_version = Column(String(50), default="1.0")
    rule_text = Column(String(1000), nullable=False)
    structured_logic = Column(JSON)
    
    severity = Column(String(20), default="medium", index=True)
    confidence_score = Column(Float, default=0.8)
    
    status = Column(SQLEnum(RuleStatus), default=RuleStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    policy = relationship("Policy", back_populates="rules")
    violations = relationship("Violation", back_populates="rule")


class Violation(Base):
    __tablename__ = "violations"

    violation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.rule_id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.policy_id", ondelete="CASCADE"), nullable=False, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    department = Column(String(100), index=True)
    severity = Column(String(20), index=True)
    
    record_id = Column(String(255))
    field_name = Column(String(255))
    field_value = Column(String(1000))
    explanation = Column(String(2000))
    evidence = Column(JSON)
    
    # Combined risk scoring
    rule_severity_score = Column(Float, default=0.0)
    anomaly_score = Column(Float, default=0.0)
    final_risk_score = Column(Float, default=0.0, index=True)
    
    status = Column(SQLEnum(ViolationStatus), default=ViolationStatus.PENDING, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    
    rule = relationship("Rule", back_populates="violations")
    policy = relationship("Policy", back_populates="violations")


class Connector(Base):
    __tablename__ = "connectors"

    connector_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    connector_name = Column(String(255), nullable=False)
    connector_type = Column(SQLEnum(ConnectorType), nullable=False)
    
    connection_config = Column(JSON)
    field_mapping = Column(JSON)
    
    status = Column(SQLEnum(ConnectorStatus), default=ConnectorStatus.INACTIVE)
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="connectors")


class Alert(Base):
    __tablename__ = "alerts_log"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.violation_id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    channel = Column(SQLEnum(AlertChannel), nullable=False)
    recipient = Column(String(255))
    
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.PENDING)
    sent_at = Column(DateTime)
    error_message = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Remediation Engine Models
class RemediationStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class RemediationPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RemediationCase(Base):
    __tablename__ = "remediation_cases"

    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.violation_id", ondelete="CASCADE"), nullable=False, unique=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.rule_id", ondelete="CASCADE"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    status = Column(SQLEnum(RemediationStatus), default=RemediationStatus.OPEN, index=True)
    priority = Column(SQLEnum(RemediationPriority), nullable=False, index=True)
    
    recommended_action = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    violation = relationship("Violation")
    rule = relationship("Rule")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    comments = relationship("RemediationComment", back_populates="case", cascade="all, delete-orphan")


class RemediationComment(Base):
    __tablename__ = "remediation_comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("remediation_cases.case_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    case = relationship("RemediationCase", back_populates="comments")
    user = relationship("User")


# Policy Change Impact Models
class ChangeType(str, enum.Enum):
    NEW = "new"
    MODIFIED = "modified"
    REMOVED = "removed"


class PolicyChangeLog(Base):
    __tablename__ = "policy_change_log"

    change_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("policies.policy_id", ondelete="CASCADE"), nullable=False, index=True)
    old_rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.rule_id"))
    new_rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.rule_id"))
    
    change_type = Column(SQLEnum(ChangeType), nullable=False)
    change_details = Column(JSON)
    
    old_violations_count = Column(Integer, default=0)
    new_violations_count = Column(Integer, default=0)
    net_risk_delta = Column(Float, default=0.0)
    
    detected_at = Column(DateTime, default=datetime.utcnow)


# Anomaly Detection Models
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(255), primary_key=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction data
    amount = Column(Float, nullable=False)
    currency = Column(String(10))
    timestamp = Column(DateTime, nullable=False)
    account_id = Column(String(255), index=True)
    
    # Risk features
    frequency_per_24h = Column(Integer, default=0)
    account_risk_score = Column(Float, default=0.0)
    transaction_velocity = Column(Float, default=0.0)
    
    # Anomaly detection
    anomaly_score = Column(Float, default=0.0, index=True)
    is_anomalous = Column(Boolean, default=False, index=True)
    
    # Metadata
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskTrend(Base):
    __tablename__ = "risk_trends"

    trend_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="CASCADE"), nullable=False, index=True)
    
    week_start = Column(DateTime, nullable=False, index=True)
    week_end = Column(DateTime, nullable=False)
    
    avg_risk_score = Column(Float, nullable=False)
    total_violations = Column(Integer, default=0)
    total_anomalies = Column(Integer, default=0)
    high_risk_accounts = Column(Integer, default=0)
    
    risk_change_percent = Column(Float, default=0.0)
    trend_direction = Column(String(20))  # increasing, decreasing, stable
    
    created_at = Column(DateTime, default=datetime.utcnow)
