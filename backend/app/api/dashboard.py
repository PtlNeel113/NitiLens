"""
Dashboard API endpoints - Feature status and aggregated data
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db
from app.models.db_models import (
    User, Policy, Rule, Violation, RemediationCase, 
    PolicyChangeLog, Transaction, Connector
)
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/feature-status")
def get_feature_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status of all enterprise features"""
    org_id = current_user.org_id
    
    # Check if features have data
    has_remediation = db.query(func.count(RemediationCase.case_id)).filter(
        RemediationCase.org_id == org_id
    ).scalar() > 0
    
    has_policy_impact = db.query(func.count(PolicyChangeLog.change_id)).scalar() > 0
    
    has_anomaly_data = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.org_id == org_id,
        Transaction.is_anomalous == True
    ).scalar() > 0
    
    has_connectors = db.query(func.count(Connector.connector_id)).filter(
        Connector.org_id == org_id
    ).scalar() > 0
    
    has_policies = db.query(func.count(Policy.policy_id)).filter(
        Policy.org_id == org_id
    ).scalar() > 0
    
    return {
        "remediation_enabled": True,  # Always available
        "policy_impact_enabled": True,  # Always available
        "anomaly_engine_enabled": True,  # Always available
        "monitoring_enabled": True,  # Always available
        "multi_policy_enabled": True,  # Always available
        "erp_connector_enabled": True,  # Always available
        "real_time_alerts_enabled": True,  # Always available
        "multilingual_enabled": True,  # Always available
        "saas_multi_tenant_enabled": True,  # Always available
        "risk_scoring_enabled": True,  # Always available
        "audit_simulation_enabled": True,  # Always available
        "root_cause_enabled": True,  # Always available
        "regulatory_mapping_enabled": True,  # Always available
        # Data availability flags
        "has_remediation_data": has_remediation,
        "has_policy_impact_data": has_policy_impact,
        "has_anomaly_data": has_anomaly_data,
        "has_connectors": has_connectors,
        "has_policies": has_policies
    }


@router.get("/overview")
def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard overview"""
    org_id = current_user.org_id
    
    # Remediation stats
    open_cases = db.query(func.count(RemediationCase.case_id)).filter(
        RemediationCase.org_id == org_id,
        RemediationCase.status.in_(["open", "in_progress"])
    ).scalar()
    
    overdue_cases = db.query(func.count(RemediationCase.case_id)).filter(
        RemediationCase.org_id == org_id,
        RemediationCase.status == "overdue"
    ).scalar()
    
    # Anomaly stats
    high_risk_anomalies = db.query(func.count(Transaction.transaction_id)).filter(
        Transaction.org_id == org_id,
        Transaction.is_anomalous == True,
        Transaction.anomaly_score > 0.85
    ).scalar()
    
    # Policy stats
    active_policies = db.query(func.count(Policy.policy_id)).filter(
        Policy.org_id == org_id,
        Policy.status == "active"
    ).scalar()
    
    # Recent policy changes
    recent_changes = db.query(func.count(PolicyChangeLog.change_id)).filter(
        PolicyChangeLog.detected_at >= datetime.utcnow() - timedelta(days=7)
    ).scalar()
    
    # Connector stats
    active_connectors = db.query(func.count(Connector.connector_id)).filter(
        Connector.org_id == org_id,
        Connector.status == "active"
    ).scalar()
    
    # Violation stats
    total_violations = db.query(func.count(Violation.violation_id)).filter(
        Violation.org_id == org_id
    ).scalar()
    
    critical_violations = db.query(func.count(Violation.violation_id)).filter(
        Violation.org_id == org_id,
        Violation.severity == "critical"
    ).scalar()
    
    return {
        "remediation": {
            "open_cases": open_cases,
            "overdue_cases": overdue_cases
        },
        "risk": {
            "high_risk_anomalies": high_risk_anomalies
        },
        "policies": {
            "active_policies": active_policies,
            "recent_changes": recent_changes
        },
        "connectors": {
            "active_connectors": active_connectors
        },
        "violations": {
            "total": total_violations,
            "critical": critical_violations
        },
        "monitoring": {
            "status": "active"
        }
    }
