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
