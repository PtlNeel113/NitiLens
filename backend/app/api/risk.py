"""
Risk & Anomaly Detection API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
import pandas as pd

from app.database import get_db
from app.models.db_models import User, Transaction
from app.auth import get_current_active_user
from app.services.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/api/risk", tags=["Risk & Anomaly Detection"])


class TrainModelRequest(BaseModel):
    connector_id: Optional[str] = None
    limit: Optional[int] = 1000


@router.post("/train-model")
async def train_anomaly_model(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Train anomaly detection model for organization"""
    detector = AnomalyDetector(db)
    
    # Fetch transaction data
    transactions = db.query(Transaction).filter(
        Transaction.org_id == current_user.org_id
    ).limit(request.limit).all()
    
    if not transactions:
        raise HTTPException(status_code=400, detail="No transaction data available")
    
    # Convert to DataFrame
    data = pd.DataFrame([
        {
            "transaction_id": t.transaction_id,
            "amount": t.amount,
            "timestamp": t.timestamp,
            "account_id": t.account_id,
            "frequency_per_24h": t.frequency_per_24h,
            "account_risk_score": t.account_risk_score,
            "transaction_velocity": t.transaction_velocity
        }
        for t in transactions
    ])
    
    # Train model in background
    result = detector.train_model(current_user.org_id, data)
    
    return result


@router.get("/anomalies")
def get_anomalies(
    threshold: float = 0.75,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detected anomalies"""
    detector = AnomalyDetector(db)
    
    anomalies = detector.get_anomalies(
        org_id=current_user.org_id,
        threshold=threshold,
        limit=limit
    )
    
    return {
        "total": len(anomalies),
        "threshold": threshold,
        "anomalies": anomalies
    }


@router.get("/heatmap")
def get_risk_heatmap(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get risk heatmap data"""
    detector = AnomalyDetector(db)
    
    heatmap = detector.generate_risk_heatmap(current_user.org_id)
    
    return heatmap


@router.get("/trend")
def get_risk_trend(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get week-over-week risk trend"""
    detector = AnomalyDetector(db)
    
    trend = detector.calculate_risk_trend(current_user.org_id)
    
    return trend


@router.get("/trends/history")
def get_risk_trends_history(
    weeks: int = 12,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get historical risk trends"""
    detector = AnomalyDetector(db)
    
    trends = detector.get_risk_trends_history(current_user.org_id, weeks)
    
    return {
        "weeks": weeks,
        "trends": trends
    }


@router.get("/dashboard")
def get_risk_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk dashboard data"""
    detector = AnomalyDetector(db)
    
    # Get all risk metrics
    anomalies = detector.get_anomalies(current_user.org_id, threshold=0.75, limit=10)
    heatmap = detector.generate_risk_heatmap(current_user.org_id)
    trend = detector.calculate_risk_trend(current_user.org_id)
    history = detector.get_risk_trends_history(current_user.org_id, weeks=8)
    
    return {
        "current_trend": trend,
        "top_anomalies": anomalies[:10],
        "risk_heatmap": heatmap,
        "historical_trends": history
    }
