"""
Enhanced background scheduler for governance features
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from app.database import SessionLocal
from app.services.remediation_engine import RemediationEngine
from app.services.anomaly_detector import AnomalyDetector
from app.models.db_models import Organization
import asyncio

scheduler = AsyncIOScheduler()


async def check_remediation_escalations():
    """Check for overdue remediation cases and escalate"""
    print(f"[{datetime.utcnow()}] Running remediation escalation check...")
    
    db = SessionLocal()
    try:
        engine = RemediationEngine(db)
        await engine.check_escalations()
        print(f"[{datetime.utcnow()}] Remediation escalation check completed")
    except Exception as e:
        print(f"Error in remediation escalation check: {e}")
    finally:
        db.close()


async def calculate_risk_trends():
    """Calculate weekly risk trends for all organizations"""
    print(f"[{datetime.utcnow()}] Calculating risk trends...")
    
    db = SessionLocal()
    try:
        # Get all organizations
        orgs = db.query(Organization).all()
        
        for org in orgs:
            detector = AnomalyDetector(db)
            trend = detector.calculate_risk_trend(org.org_id)
            print(f"Org {org.org_name}: Risk trend {trend['trend']}")
        
        print(f"[{datetime.utcnow()}] Risk trend calculation completed")
    except Exception as e:
        print(f"Error in risk trend calculation: {e}")
    finally:
        db.close()


def start_enhanced_scheduler():
    """Start the enhanced background scheduler"""
    # Check remediation escalations every hour
    scheduler.add_job(
        check_remediation_escalations,
        CronTrigger(minute=0),  # Every hour at minute 0
        id="remediation_escalation_check",
        replace_existing=True
    )
    
    # Calculate risk trends every Monday at 1 AM
    scheduler.add_job(
        calculate_risk_trends,
        CronTrigger(day_of_week='mon', hour=1, minute=0),
        id="risk_trend_calculation",
        replace_existing=True
    )
    
    scheduler.start()
    print("✅ Enhanced governance scheduler started")


def stop_enhanced_scheduler():
    """Stop the enhanced background scheduler"""
    scheduler.shutdown()
    print("👋 Enhanced governance scheduler stopped")
