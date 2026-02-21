"""
Initialize database with schema and seed data
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.db_models import Organization, User, SubscriptionPlan, UserRole
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
        # Check if demo org exists
        demo_org = db.query(Organization).filter(Organization.org_name == "Demo Organization").first()
        
        if not demo_org:
            print("🌱 Seeding default data...")
            
            # Create demo organization
            demo_org = Organization(
                org_name="Demo Organization",
                subscription_plan=SubscriptionPlan.PRO,
                policy_limit="10",
                transaction_limit="1000000"
            )
            db.add(demo_org)
            db.flush()
            
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
