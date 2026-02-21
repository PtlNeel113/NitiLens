"""
Initialize database with schema and seed data
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.database import Base
from app.models.db_models import (
    Organization, User, SubscriptionPlan, UserRole,
    Plan, Subscription, SubscriptionStatus
)
from app.auth import get_password_hash
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nitilens:nitilens_password@localhost:5432/nitilens_db")

def init_database():
    """Initialize database schema and seed data"""
    print("🔧 Initializing database...")
    
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    print("📊 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Seed default data
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Seed subscription plans first
        print("\n🌱 Seeding subscription plans...")
        existing_plans = db.query(Plan).count()
        
        if existing_plans == 0:
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
                price_monthly=0.00
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
                max_policies=-1,
                max_transactions_per_month=-1,
                max_users=-1,
                anomaly_detection_enabled=True,
                remediation_enabled=True,
                regulatory_mapping_enabled=True,
                monitoring_enabled=True,
                policy_impact_enabled=True,
                multi_language_enabled=True,
                price_monthly=999.00
            )
            db.add(enterprise_plan)
            
            db.flush()
            print("✅ Subscription plans created")
        else:
            print("ℹ️  Subscription plans already exist")
            pro_plan = db.query(Plan).filter(Plan.name == SubscriptionPlan.PRO).first()
        
        # Check if demo org exists
        demo_org = db.query(Organization).filter(Organization.org_name == "Demo Organization").first()
        
        if not demo_org:
            print("\n🌱 Seeding default data...")
            
            # Create demo organization
            demo_org = Organization(
                org_name="Demo Organization",
                subscription_plan=SubscriptionPlan.PRO,
                policy_limit="10",
                transaction_limit="1000000"
            )
            db.add(demo_org)
            db.flush()
            
            # Create subscription for demo org
            subscription = Subscription(
                org_id=demo_org.org_id,
                plan_id=pro_plan.plan_id,
                status=SubscriptionStatus.ACTIVE,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=365),
                auto_renew=True
            )
            db.add(subscription)
            
            # Create admin user
            admin_user = User(
                email="admin@nitilens.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                org_id=demo_org.org_id,
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            db.add(admin_user)
            
            # Create demo user
            demo_user = User(
                email="demo@nitilens.com",
                hashed_password=get_password_hash("demo123"),
                full_name="Demo User",
                org_id=demo_org.org_id,
                role=UserRole.COMPLIANCE_ADMIN,
                is_active=True
            )
            db.add(demo_user)
            
            db.commit()
            
            print("✅ Default data seeded successfully")
            print("\n📝 Default credentials:")
            print("   Admin: admin@nitilens.com / admin123")
            print("   Demo:  demo@nitilens.com / demo123")
            print("\n💳 Subscription:")
            print("   Plan: Pro")
            print("   Limits: 10 policies, 1M transactions/month, 20 users")
        else:
            print("ℹ️  Database already initialized")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("\n✅ Database initialization complete!")


if __name__ == "__main__":
    init_database()
