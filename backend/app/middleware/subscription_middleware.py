"""
Subscription enforcement middleware
"""
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.db_models import User
from app.auth import get_current_active_user
from app.services.subscription_service import SubscriptionService


def require_feature(feature_name: str):
    """Decorator to require a specific feature to be enabled"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        service = SubscriptionService(db)
        result = service.check_feature_enabled(current_user.org_id, feature_name)
        
        if not result.get("enabled"):
            raise HTTPException(
                status_code=403,
                detail=result.get("reason", f"Feature '{feature_name}' not available in your plan")
            )
        
        return current_user
    
    return dependency


def check_policy_limit(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if organization can upload more policies"""
    service = SubscriptionService(db)
    result = service.check_policy_limit(current_user.org_id)
    
    if not result.get("allowed"):
        raise HTTPException(
            status_code=403,
            detail=result.get("reason", "Policy limit exceeded. Upgrade your plan.")
        )
    
    return current_user


def check_transaction_limit(transaction_count: int = 1):
    """Check if organization can scan more transactions"""
    def dependency(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ):
        service = SubscriptionService(db)
        result = service.check_transaction_limit(current_user.org_id, transaction_count)
        
        if not result.get("allowed"):
            raise HTTPException(
                status_code=403,
                detail=result.get("reason", "Monthly transaction limit exceeded. Upgrade your plan.")
            )
        
        return current_user
    
    return dependency


def check_user_limit(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if organization can add more users"""
    service = SubscriptionService(db)
    result = service.check_user_limit(current_user.org_id)
    
    if not result.get("allowed"):
        raise HTTPException(
            status_code=403,
            detail=result.get("reason", "User limit exceeded. Upgrade your plan.")
        )
    
    return current_user
