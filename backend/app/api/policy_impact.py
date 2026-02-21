"""
Policy Impact Analysis API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.db_models import User
from app.auth import get_current_active_user
from app.services.policy_impact_analyzer import PolicyImpactAnalyzer
from app.middleware.subscription_middleware import require_feature

router = APIRouter(prefix="/api/policy-impact", tags=["Policy Impact"])


class CompareRequest(BaseModel):
    old_policy_id: str
    new_policy_id: str


@router.post("/analyze")
def analyze_policy_change(
    request: CompareRequest,
    current_user: User = Depends(require_feature("policy_impact")),
    db: Session = Depends(get_db)
):
    """Analyze impact of policy change"""
    analyzer = PolicyImpactAnalyzer(db)
    
    try:
        old_policy_id = UUID(request.old_policy_id)
        new_policy_id = UUID(request.new_policy_id)
        
        impact = analyzer.analyze_policy_update(old_policy_id, new_policy_id)
        
        return impact
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{policy_id}")
def get_policy_change_history(
    policy_id: UUID,
    current_user: User = Depends(require_feature("policy_impact")),
    db: Session = Depends(get_db)
):
    """Get change history for a policy"""
    analyzer = PolicyImpactAnalyzer(db)
    
    history = analyzer.get_policy_history(policy_id)
    
    return {
        "policy_id": str(policy_id),
        "changes": history
    }


@router.get("/report/{policy_id}")
def get_impact_report(
    policy_id: UUID,
    current_user: User = Depends(require_feature("policy_impact")),
    db: Session = Depends(get_db)
):
    """Get comprehensive impact report for policy"""
    from app.models.db_models import Policy, PolicyChangeLog
    
    policy = db.query(Policy).filter(
        Policy.policy_id == policy_id,
        Policy.org_id == current_user.org_id
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    # Get all changes
    changes = db.query(PolicyChangeLog).filter(
        PolicyChangeLog.policy_id == policy_id
    ).order_by(PolicyChangeLog.detected_at.desc()).all()
    
    # Aggregate impact
    total_new_violations = sum(c.new_violations_count for c in changes)
    total_old_violations = sum(c.old_violations_count for c in changes)
    total_net_delta = sum(c.net_risk_delta for c in changes)
    
    return {
        "policy_id": str(policy_id),
        "policy_name": policy.policy_name,
        "version": policy.version,
        "total_changes": len(changes),
        "summary": {
            "total_new_violations": total_new_violations,
            "total_old_violations": total_old_violations,
            "net_risk_delta": total_net_delta,
            "risk_direction": "increased" if total_net_delta > 0 else "decreased" if total_net_delta < 0 else "stable"
        },
        "changes": [
            {
                "change_id": str(c.change_id),
                "change_type": c.change_type.value,
                "old_violations": c.old_violations_count,
                "new_violations": c.new_violations_count,
                "net_delta": c.net_risk_delta,
                "detected_at": c.detected_at.isoformat(),
                "details": c.change_details
            }
            for c in changes
        ]
    }
