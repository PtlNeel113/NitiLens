"""
Celery worker for background tasks
"""
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
celery_app = Celery(
    "nitilens",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
)


@celery_app.task(name="scan_compliance")
def scan_compliance_task(org_id: str, connector_id: str = None, limit: int = None):
    """Background task for compliance scanning"""
    from app.database import SessionLocal
    from app.services.compliance_engine import ComplianceEngine
    import asyncio
    
    db = SessionLocal()
    try:
        engine = ComplianceEngine(db)
        result = asyncio.run(engine.scan_all_policies(
            org_id=org_id,
            connector_id=connector_id,
            limit=limit
        ))
        return result
    finally:
        db.close()


@celery_app.task(name="process_policy")
def process_policy_task(policy_id: str):
    """Background task for policy processing"""
    from app.database import SessionLocal
    from app.models.db_models import Policy
    from app.services.translation_service import translation_service
    from app.core.rule_extractor import extract_rules_from_policy
    
    db = SessionLocal()
    try:
        policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
        if not policy:
            return {"error": "Policy not found"}
        
        # Process translation if needed
        # Extract rules
        # Update policy status
        
        return {"status": "success", "policy_id": policy_id}
    finally:
        db.close()


@celery_app.task(name="send_scheduled_report")
def send_scheduled_report_task(org_id: str, report_type: str):
    """Background task for scheduled reports"""
    from app.database import SessionLocal
    from app.services.alert_service import alert_service
    
    db = SessionLocal()
    try:
        # Generate and send report
        return {"status": "success", "report_type": report_type}
    finally:
        db.close()


if __name__ == "__main__":
    celery_app.start()
