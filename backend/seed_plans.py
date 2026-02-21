"""
Seed default subscription plans
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from dotenv import load_dotenv

from app.database import Base
from app.models.db_models import Plan, Subscription, SubscriptionPlan, SubscriptionStatus, Organization

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db")


def seed_plans():
    """Seed default subscription plans"""
    print("🌱 Seeding subscription plans...")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if plans already exist
        existing_plans = db.query(Plan).count()
        if existing_plans > 0:
            print("ℹ️  Plans already exist, skipping...")
            return
        
        # Create Basic Plan
        basic_plan = Plan(
            name=SubscriptionPlan.BASIC,
            max_policies=1,
            max_transactions_per_month=10000,
            max_users=3,
            anomaly_detection_enabled=False,
            remediation_enabled=False,
            regulatory_mapping_enabled=False,
            monitoring_enabled=False,
            policy_impact_enabled=False,
            multi_language_enabled=False,
            price_monthly=0.00  # Free tier
        )
        db.add(basic_plan)
        
        # Create Pro Plan
        pro_plan = Plan(
            name=SubscriptionPlan.PRO,
            max_policies=10,
            max_transactions_per_month=1000000,
            max_users=20,
            anomaly_detection_enabled=True,
            remediation_enabled=True,
            regulatory_mapping_enabled=True,
            monitoring_enabled=True,
            policy_impact_enabled=True,
            multi_language_enabled=True,
            price_monthly=299.00
        )
        db.add(pro_plan)
        
        # Create Enterprise Plan
        enterprise_plan = Plan(
            name=SubscriptionPlan.ENTERPRISE,
            max_policies=-1,  # Unlimited
            max_transactions_per_month=-1,  # Unlimited
            max_users=-1,  # Unlimited
            anomaly_detection_enabled=True,
            remediation_enabled=True,
            regulatory_mapping_enabled=True,
            monitoring_enabled=True,
            policy_impact_enabled=True,
            multi_language_enabled=True,
            price_monthly=999.00
        )
        db.add(enterprise_plan)
        
        db.commit()
        
        print("✅ Plans created successfully:")
        print(f"   - Basic: $0/month (1 policy, 10K transactions, 3 users)")
        print(f"   - Pro: $299/month (10 policies, 1M transactions, 20 users)")
        print(f"   - Enterprise: $999/month (unlimited)")
        
        # Assign subscriptions to existing organizations
        print("\n🔗 Assigning subscriptions to existing organizations...")
        
        organizations = db.query(Organization).all()
        
        for org in organizations:
            # Check if subscription already exists
            existing_sub = db.query(Subscription).filter(
                Subscription.org_id == org.org_id
            ).first()
            
            if existing_sub:
                print(f"   ℹ️  {org.org_name} already has a subscription")
                continue
            
            # Assign Pro plan by default for demo
            subscription = Subscription(
                org_id=org.org_id,
                plan_id=pro_plan.plan_id,
                status=SubscriptionStatus.ACTIVE,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year
                auto_renew=True
            )
            db.add(subscription)
            print(f"   ✅ Assigned Pro plan to {org.org_name}")
        
        db.commit()
        
        print("\n✅ Subscription setup complete!")
        
    except Exception as e:
        print(f"❌ Error seeding plans: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_plans()
