"""
Subscription API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db_models import User, SubscriptionPlan
from app.auth import get_current_active_user
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


class UpgradeRequest(BaseModel):
    plan_name: str


@router.get("/current")
def get_current_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current subscription details"""
    service = SubscriptionService(db)
    
    subscription = service.get_organization_subscription(current_user.org_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")
    
    plan = service.get_plan(subscription.plan_id)
    
    return {
        "subscription_id": str(subscription.subscription_id),
        "plan": {
            "name": plan.name.value,
            "max_policies": plan.max_policies if plan.max_policies != -1 else "unlimited",
            "max_transactions_per_month": plan.max_transactions_per_month if plan.max_transactions_per_month != -1 else "unlimited",
            "max_users": plan.max_users if plan.max_users != -1 else "unlimited",
            "price_monthly": plan.price_monthly,
            "features": {
                "anomaly_detection": plan.anomaly_detection_enabled,
                "remediation": plan.remediation_enabled,
                "regulatory_mapping": plan.regulatory_mapping_enabled,
                "monitoring": plan.monitoring_enabled,
                "policy_impact": plan.policy_impact_enabled,
                "multi_language": plan.multi_language_enabled
            }
        },
        "status": subscription.status.value,
        "started_at": subscription.started_at.isoformat(),
        "expires_at": subscription.expires_at.isoformat(),
        "auto_renew": subscription.auto_renew
    }


@router.get("/usage")
def get_usage(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current usage and limits"""
    service = SubscriptionService(db)
    
    summary = service.get_usage_summary(current_user.org_id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary


@router.post("/upgrade")
def upgrade_subscription(
    request: UpgradeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upgrade to a different plan"""
    # Validate plan name
    try:
        plan_name = SubscriptionPlan(request.plan_name.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan name")
    
    service = SubscriptionService(db)
    result = service.upgrade_subscription(current_user.org_id, plan_name)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/cancel")
def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel subscription (will not auto-renew)"""
    service = SubscriptionService(db)
    result = service.cancel_subscription(current_user.org_id)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    """List all available plans"""
    from app.models.db_models import Plan
    
    plans = db.query(Plan).all()
    
    return [
        {
            "plan_id": str(plan.plan_id),
            "name": plan.name.value,
            "max_policies": plan.max_policies if plan.max_policies != -1 else "unlimited",
            "max_transactions_per_month": plan.max_transactions_per_month if plan.max_transactions_per_month != -1 else "unlimited",
            "max_users": plan.max_users if plan.max_users != -1 else "unlimited",
            "price_monthly": plan.price_monthly,
            "features": {
                "anomaly_detection": plan.anomaly_detection_enabled,
                "remediation": plan.remediation_enabled,
                "regulatory_mapping": plan.regulatory_mapping_enabled,
                "monitoring": plan.monitoring_enabled,
                "policy_impact": plan.policy_impact_enabled,
                "multi_language": plan.multi_language_enabled
            }
        }
        for plan in plans
    ]
