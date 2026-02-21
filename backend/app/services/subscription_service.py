"""
Subscription Service - Enforce plan limits and track usage
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from app.models.db_models import (
    Organization, Subscription, Plan, UsageTracking,
    SubscriptionPlan, SubscriptionStatus, User, Policy
)


class SubscriptionService:
    """Service to manage subscriptions and enforce limits"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_organization_subscription(self, org_id: UUID) -> Optional[Subscription]:
        """Get active subscription for organization"""
        return self.db.query(Subscription).filter(
            Subscription.org_id == org_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    def get_plan(self, plan_id: UUID) -> Optional[Plan]:
        """Get plan details"""
        return self.db.query(Plan).filter(Plan.plan_id == plan_id).first()
    
    def get_plan_by_name(self, plan_name: SubscriptionPlan) -> Optional[Plan]:
        """Get plan by name"""
        return self.db.query(Plan).filter(Plan.name == plan_name).first()
    
    def get_current_month_usage(self, org_id: UUID) -> Optional[UsageTracking]:
        """Get usage for current month"""
        # Get first day of current month
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        usage = self.db.query(UsageTracking).filter(
            UsageTracking.org_id == org_id,
            UsageTracking.month == month_start
        ).first()
        
        # Create if doesn't exist
        if not usage:
            usage = UsageTracking(
                org_id=org_id,
                month=month_start,
                transactions_scanned=0,
                policies_uploaded=0,
                users_count=0
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def check_policy_limit(self, org_id: UUID) -> Dict[str, Any]:
        """Check if organization can upload more policies"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"allowed": False, "reason": "No active subscription"}
        
        plan = self.get_plan(subscription.plan_id)
        if not plan:
            return {"allowed": False, "reason": "Invalid plan"}
        
        # Count current policies
        current_policies = self.db.query(func.count(Policy.policy_id)).filter(
            Policy.org_id == org_id,
            Policy.status == "active"
        ).scalar()
        
        # Check limit (-1 means unlimited)
        if plan.max_policies == -1:
            return {
                "allowed": True,
                "current": current_policies,
                "limit": "unlimited"
            }
        
        if current_policies >= plan.max_policies:
            return {
                "allowed": False,
                "reason": f"Policy limit exceeded. Current: {current_policies}, Limit: {plan.max_policies}",
                "current": current_policies,
                "limit": plan.max_policies
            }
        
        return {
            "allowed": True,
            "current": current_policies,
            "limit": plan.max_policies
        }
    
    def check_transaction_limit(self, org_id: UUID, transaction_count: int = 1) -> Dict[str, Any]:
        """Check if organization can scan more transactions"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"allowed": False, "reason": "No active subscription"}
        
        plan = self.get_plan(subscription.plan_id)
        if not plan:
            return {"allowed": False, "reason": "Invalid plan"}
        
        usage = self.get_current_month_usage(org_id)
        
        # Check limit (-1 means unlimited)
        if plan.max_transactions_per_month == -1:
            return {
                "allowed": True,
                "current": usage.transactions_scanned,
                "limit": "unlimited"
            }
        
        if usage.transactions_scanned + transaction_count > plan.max_transactions_per_month:
            return {
                "allowed": False,
                "reason": f"Monthly transaction limit exceeded. Current: {usage.transactions_scanned}, Limit: {plan.max_transactions_per_month}",
                "current": usage.transactions_scanned,
                "limit": plan.max_transactions_per_month
            }
        
        return {
            "allowed": True,
            "current": usage.transactions_scanned,
            "limit": plan.max_transactions_per_month
        }
    
    def check_user_limit(self, org_id: UUID) -> Dict[str, Any]:
        """Check if organization can add more users"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"allowed": False, "reason": "No active subscription"}
        
        plan = self.get_plan(subscription.plan_id)
        if not plan:
            return {"allowed": False, "reason": "Invalid plan"}
        
        # Count current users
        current_users = self.db.query(func.count(User.user_id)).filter(
            User.org_id == org_id,
            User.is_active == True
        ).scalar()
        
        # Check limit (-1 means unlimited)
        if plan.max_users == -1:
            return {
                "allowed": True,
                "current": current_users,
                "limit": "unlimited"
            }
        
        if current_users >= plan.max_users:
            return {
                "allowed": False,
                "reason": f"User limit exceeded. Current: {current_users}, Limit: {plan.max_users}",
                "current": current_users,
                "limit": plan.max_users
            }
        
        return {
            "allowed": True,
            "current": current_users,
            "limit": plan.max_users
        }
    
    def check_feature_enabled(self, org_id: UUID, feature: str) -> Dict[str, Any]:
        """Check if a feature is enabled for organization's plan"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"enabled": False, "reason": "No active subscription"}
        
        plan = self.get_plan(subscription.plan_id)
        if not plan:
            return {"enabled": False, "reason": "Invalid plan"}
        
        feature_map = {
            "anomaly_detection": plan.anomaly_detection_enabled,
            "remediation": plan.remediation_enabled,
            "regulatory_mapping": plan.regulatory_mapping_enabled,
            "monitoring": plan.monitoring_enabled,
            "policy_impact": plan.policy_impact_enabled,
            "multi_language": plan.multi_language_enabled
        }
        
        if feature not in feature_map:
            return {"enabled": False, "reason": "Unknown feature"}
        
        enabled = feature_map[feature]
        
        if not enabled:
            return {
                "enabled": False,
                "reason": f"Feature '{feature}' not available in {plan.name.value} plan. Upgrade required."
            }
        
        return {"enabled": True}
    
    def increment_transaction_usage(self, org_id: UUID, count: int = 1):
        """Increment transaction usage counter"""
        usage = self.get_current_month_usage(org_id)
        usage.transactions_scanned += count
        usage.updated_at = datetime.utcnow()
        self.db.commit()
    
    def increment_policy_usage(self, org_id: UUID):
        """Increment policy usage counter"""
        usage = self.get_current_month_usage(org_id)
        usage.policies_uploaded += 1
        usage.updated_at = datetime.utcnow()
        self.db.commit()
    
    def update_user_count(self, org_id: UUID):
        """Update user count in usage tracking"""
        usage = self.get_current_month_usage(org_id)
        
        # Count active users
        user_count = self.db.query(func.count(User.user_id)).filter(
            User.org_id == org_id,
            User.is_active == True
        ).scalar()
        
        usage.users_count = user_count
        usage.updated_at = datetime.utcnow()
        self.db.commit()
    
    def get_usage_summary(self, org_id: UUID) -> Dict[str, Any]:
        """Get comprehensive usage summary"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"error": "No active subscription"}
        
        plan = self.get_plan(subscription.plan_id)
        usage = self.get_current_month_usage(org_id)
        
        # Count current resources
        current_policies = self.db.query(func.count(Policy.policy_id)).filter(
            Policy.org_id == org_id,
            Policy.status == "active"
        ).scalar()
        
        current_users = self.db.query(func.count(User.user_id)).filter(
            User.org_id == org_id,
            User.is_active == True
        ).scalar()
        
        return {
            "plan": {
                "name": plan.name.value,
                "price_monthly": plan.price_monthly
            },
            "subscription": {
                "status": subscription.status.value,
                "started_at": subscription.started_at.isoformat(),
                "expires_at": subscription.expires_at.isoformat(),
                "auto_renew": subscription.auto_renew
            },
            "limits": {
                "policies": {
                    "current": current_policies,
                    "limit": plan.max_policies if plan.max_policies != -1 else "unlimited",
                    "percentage": (current_policies / plan.max_policies * 100) if plan.max_policies != -1 else 0
                },
                "transactions": {
                    "current": usage.transactions_scanned,
                    "limit": plan.max_transactions_per_month if plan.max_transactions_per_month != -1 else "unlimited",
                    "percentage": (usage.transactions_scanned / plan.max_transactions_per_month * 100) if plan.max_transactions_per_month != -1 else 0
                },
                "users": {
                    "current": current_users,
                    "limit": plan.max_users if plan.max_users != -1 else "unlimited",
                    "percentage": (current_users / plan.max_users * 100) if plan.max_users != -1 else 0
                }
            },
            "features": {
                "anomaly_detection": plan.anomaly_detection_enabled,
                "remediation": plan.remediation_enabled,
                "regulatory_mapping": plan.regulatory_mapping_enabled,
                "monitoring": plan.monitoring_enabled,
                "policy_impact": plan.policy_impact_enabled,
                "multi_language": plan.multi_language_enabled
            }
        }
    
    def upgrade_subscription(self, org_id: UUID, new_plan_name: SubscriptionPlan) -> Dict[str, Any]:
        """Upgrade organization to new plan"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"success": False, "error": "No active subscription"}
        
        new_plan = self.get_plan_by_name(new_plan_name)
        if not new_plan:
            return {"success": False, "error": "Invalid plan"}
        
        old_plan = self.get_plan(subscription.plan_id)
        
        # Update subscription
        subscription.plan_id = new_plan.plan_id
        subscription.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "message": f"Upgraded from {old_plan.name.value} to {new_plan.name.value}",
            "old_plan": old_plan.name.value,
            "new_plan": new_plan.name.value
        }
    
    def cancel_subscription(self, org_id: UUID) -> Dict[str, Any]:
        """Cancel subscription (will expire at end of period)"""
        subscription = self.get_organization_subscription(org_id)
        if not subscription:
            return {"success": False, "error": "No active subscription"}
        
        subscription.auto_renew = False
        subscription.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return {
            "success": True,
            "message": "Subscription will not auto-renew",
            "expires_at": subscription.expires_at.isoformat()
        }
    
    def reset_monthly_usage(self, org_id: UUID):
        """Reset usage counters for new month (called by background job)"""
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        
        # Check if usage record exists for current month
        existing = self.db.query(UsageTracking).filter(
            UsageTracking.org_id == org_id,
            UsageTracking.month == month_start
        ).first()
        
        if not existing:
            # Create new usage record for current month
            usage = UsageTracking(
                org_id=org_id,
                month=month_start,
                transactions_scanned=0,
                policies_uploaded=0,
                users_count=0
            )
            self.db.add(usage)
            self.db.commit()
