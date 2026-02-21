"""
Monitoring and health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
from datetime import datetime, timedelta

from app.database import get_db
from app.models.db_models import Policy, Rule, Violation, Organization, User
from app.middleware.subscription_middleware import require_feature
from app.auth import get_current_active_user

router = APIRouter(tags=["Monitoring"])

# Prometheus metrics
scan_counter = Counter('compliance_scans_total', 'Total compliance scans')
violation_counter = Counter('violations_detected_total', 'Total violations detected', ['severity'])
scan_duration = Histogram('scan_duration_seconds', 'Scan duration in seconds')


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "NitiLens Compliance Platform",
            "version": "2.0.0",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/api/performance/metrics")
def performance_metrics_endpoint():
    """Get API performance metrics"""
    from app.middleware.performance_middleware import performance_metrics
    
    summary = performance_metrics.get_summary()
    
    # Add system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        "api_performance": summary,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics"""
    # Count organizations
    total_orgs = db.query(func.count(Organization.org_id)).scalar()
    
    # Count users
    total_users = db.query(func.count(User.user_id)).scalar()
    
    # Count policies
    total_policies = db.query(func.count(Policy.policy_id)).scalar()
    active_policies = db.query(func.count(Policy.policy_id)).filter(
        Policy.status == "active"
    ).scalar()
    
    # Count rules
    total_rules = db.query(func.count(Rule.rule_id)).scalar()
    
    # Count violations
    total_violations = db.query(func.count(Violation.violation_id)).scalar()
    
    # Violations by severity
    violations_by_severity = {}
    for severity in ["critical", "high", "medium", "low"]:
        count = db.query(func.count(Violation.violation_id)).filter(
            Violation.severity == severity
        ).scalar()
        violations_by_severity[severity] = count
    
    # Recent violations (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_violations = db.query(func.count(Violation.violation_id)).filter(
        Violation.detected_at >= yesterday
    ).scalar()
    
    return {
        "organizations": total_orgs,
        "users": total_users,
        "policies": {
            "total": total_policies,
            "active": active_policies
        },
        "rules": total_rules,
        "violations": {
            "total": total_violations,
            "recent_24h": recent_violations,
            "by_severity": violations_by_severity
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/api/system/info")
def system_info(current_user: User = Depends(require_feature("monitoring"))):
    """Get system information"""
    import platform
    import psutil
    
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
        "disk_usage_percent": psutil.disk_usage('/').percent
    }


@router.get("/api/system/integrity-check")
def integrity_check(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Single Source of Truth Validation
    Validates that dashboard metrics match database counts
    """
    from app.models.db_models import RemediationCase
    
    mismatches = []
    
    # Count violations in DB
    db_violations_count = db.query(func.count(Violation.violation_id)).filter(
        Violation.org_id == current_user.org_id
    ).scalar()
    
    # Count high/critical violations
    high_critical_count = db.query(func.count(Violation.violation_id)).filter(
        Violation.org_id == current_user.org_id,
        Violation.severity.in_(["high", "critical"])
    ).scalar()
    
    # Count remediation cases
    remediation_count = db.query(func.count(RemediationCase.case_id)).filter(
        RemediationCase.org_id == current_user.org_id
    ).scalar()
    
    # Count active policies
    active_policies = db.query(func.count(Policy.policy_id)).filter(
        Policy.org_id == current_user.org_id,
        Policy.status == "active"
    ).scalar()
    
    # Count approved rules
    approved_rules = db.query(func.count(Rule.rule_id)).filter(
        Rule.org_id == current_user.org_id,
        Rule.status == "approved"
    ).scalar()
    
    # Validate: Remediation cases should match high/critical violations
    if remediation_count != high_critical_count:
        mismatches.append({
            "check": "remediation_vs_violations",
            "expected": high_critical_count,
            "actual": remediation_count,
            "message": f"Remediation cases ({remediation_count}) don't match high/critical violations ({high_critical_count})"
        })
    
    # Validate: All policies should have rules
    if active_policies > 0 and approved_rules == 0:
        mismatches.append({
            "check": "policies_vs_rules",
            "expected": f"> 0 rules for {active_policies} policies",
            "actual": 0,
            "message": "Active policies exist but no approved rules found"
        })
    
    # Calculate compliance rate consistency
    if db_violations_count > 0:
        # Get total transactions scanned (from usage tracking or violations)
        total_transactions = db.query(func.count(Violation.transaction_id.distinct())).filter(
            Violation.org_id == current_user.org_id
        ).scalar()
        
        if total_transactions > 0:
            calculated_compliance_rate = ((total_transactions - db_violations_count) / total_transactions) * 100
        else:
            calculated_compliance_rate = 100.0
    else:
        calculated_compliance_rate = 100.0
    
    status = "healthy" if len(mismatches) == 0 else "inconsistent"
    
    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "org_id": str(current_user.org_id),
        "counts": {
            "violations": db_violations_count,
            "high_critical_violations": high_critical_count,
            "remediation_cases": remediation_count,
            "active_policies": active_policies,
            "approved_rules": approved_rules
        },
        "calculated_metrics": {
            "compliance_rate": round(calculated_compliance_rate, 2)
        },
        "mismatch_details": mismatches,
        "checks_passed": len(mismatches) == 0
    }
