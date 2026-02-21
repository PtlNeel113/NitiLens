"""
Predictive Risk & Anomaly Detection
ML-based anomaly detection using Isolation Forest
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from uuid import UUID
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

from app.models.db_models import Transaction, Violation, RiskTrend


class AnomalyDetector:
    """ML-based anomaly detection and risk prediction"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {}  # Cache models per org
        self.scalers = {}  # Cache scalers per org
        self.model_dir = "models/anomaly"
        os.makedirs(self.model_dir, exist_ok=True)
    
    def train_model(self, org_id: UUID, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Train Isolation Forest model for organization
        """
        if len(data) < 100:
            return {
                "status": "insufficient_data",
                "message": "Need at least 100 transactions to train model",
                "records": len(data)
            }
        
        # Extract features
        features = self._extract_features(data)
        
        if features.empty:
            return {
                "status": "error",
                "message": "Failed to extract features"
            }
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # Expect 10% anomalies
            random_state=42,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1
        )
        
        model.fit(features_scaled)
        
        # Cache model and scaler
        self.models[str(org_id)] = model
        self.scalers[str(org_id)] = scaler
        
        # Save to disk
        model_path = os.path.join(self.model_dir, f"{org_id}_model.pkl")
        scaler_path = os.path.join(self.model_dir, f"{org_id}_scaler.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        return {
            "status": "success",
            "message": "Model trained successfully",
            "records": len(data),
            "features": list(features.columns)
        }
    
    def _extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for anomaly detection"""
        features = pd.DataFrame()
        
        # Transaction amount (log scale to handle outliers)
        if 'amount' in data.columns:
            features['log_amount'] = np.log1p(data['amount'])
            features['amount_zscore'] = (data['amount'] - data['amount'].mean()) / data['amount'].std()
        
        # Frequency per 24h
        if 'frequency_per_24h' in data.columns:
            features['frequency_per_24h'] = data['frequency_per_24h']
        elif 'account_id' in data.columns and 'timestamp' in data.columns:
            # Calculate frequency
            freq = data.groupby('account_id').size()
            features['frequency_per_24h'] = data['account_id'].map(freq)
        else:
            features['frequency_per_24h'] = 0
        
        # Account risk score
        if 'account_risk_score' in data.columns:
            features['account_risk_score'] = data['account_risk_score']
        else:
            features['account_risk_score'] = 0.5  # Default medium risk
        
        # Transaction velocity (amount per hour)
        if 'transaction_velocity' in data.columns:
            features['transaction_velocity'] = data['transaction_velocity']
        elif 'amount' in data.columns and 'frequency_per_24h' in features.columns:
            features['transaction_velocity'] = data['amount'] / (features['frequency_per_24h'] + 1)
        else:
            features['transaction_velocity'] = 0
        
        # Time-based features
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            features['hour_of_day'] = data['timestamp'].dt.hour
            features['day_of_week'] = data['timestamp'].dt.dayofweek
            features['is_weekend'] = (data['timestamp'].dt.dayofweek >= 5).astype(int)
        
        return features
    
    def detect_anomalies(self, org_id: UUID, data: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in transaction data
        Returns data with anomaly scores and flags
        """
        # Load or train model
        model = self._load_model(org_id)
        scaler = self._load_scaler(org_id)
        
        if model is None or scaler is None:
            # Train new model
            train_result = self.train_model(org_id, data)
            if train_result["status"] != "success":
                # Return data with default scores
                data['anomaly_score'] = 0.0
                data['is_anomalous'] = False
                return data
            
            model = self.models[str(org_id)]
            scaler = self.scalers[str(org_id)]
        
        # Extract features
        features = self._extract_features(data)
        
        if features.empty:
            data['anomaly_score'] = 0.0
            data['is_anomalous'] = False
            return data
        
        # Normalize
        features_scaled = scaler.transform(features)
        
        # Predict anomaly scores
        # Isolation Forest returns -1 for anomalies, 1 for normal
        predictions = model.predict(features_scaled)
        decision_scores = model.decision_function(features_scaled)
        
        # Convert to 0-1 scale (higher = more anomalous)
        # decision_function returns negative values for anomalies
        anomaly_scores = 1 / (1 + np.exp(decision_scores))  # Sigmoid transformation
        
        # Clip to 0-1 range
        anomaly_scores = np.clip(anomaly_scores, 0, 1)
        
        # Add to dataframe
        data['anomaly_score'] = anomaly_scores
        data['is_anomalous'] = (anomaly_scores > 0.75).astype(bool)
        
        return data
    
    def _load_model(self, org_id: UUID):
        """Load cached or saved model"""
        org_id_str = str(org_id)
        
        # Check cache
        if org_id_str in self.models:
            return self.models[org_id_str]
        
        # Load from disk
        model_path = os.path.join(self.model_dir, f"{org_id}_model.pkl")
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
                self.models[org_id_str] = model
                return model
        
        return None
    
    def _load_scaler(self, org_id: UUID):
        """Load cached or saved scaler"""
        org_id_str = str(org_id)
        
        # Check cache
        if org_id_str in self.scalers:
            return self.scalers[org_id_str]
        
        # Load from disk
        scaler_path = os.path.join(self.model_dir, f"{org_id}_scaler.pkl")
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
                self.scalers[org_id_str] = scaler
                return scaler
        
        return None
    
    def calculate_combined_risk_score(
        self,
        rule_severity: str,
        anomaly_score: float
    ) -> float:
        """
        Calculate combined risk score
        70% rule-based + 30% anomaly-based
        """
        # Map severity to score (0-100)
        severity_scores = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        rule_score = severity_scores.get(rule_severity.lower(), 50)
        
        # Combined score
        final_score = (rule_score * 0.7) + (anomaly_score * 100 * 0.3)
        
        return round(final_score, 2)
    
    def get_anomalies(
        self,
        org_id: UUID,
        threshold: float = 0.75,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get detected anomalies"""
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.org_id == org_id,
                Transaction.is_anomalous == True,
                Transaction.anomaly_score >= threshold
            )
        ).order_by(Transaction.anomaly_score.desc()).limit(limit).all()
        
        return [
            {
                "transaction_id": t.transaction_id,
                "amount": t.amount,
                "anomaly_score": t.anomaly_score,
                "account_id": t.account_id,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "risk_level": self._score_to_risk_level(t.anomaly_score)
            }
            for t in transactions
        ]
    
    def _score_to_risk_level(self, score: float) -> str:
        """Convert anomaly score to risk level"""
        if score >= 0.9:
            return "critical"
        elif score >= 0.75:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def generate_risk_heatmap(self, org_id: UUID) -> Dict[str, Any]:
        """Generate risk heatmap data"""
        # Get transactions with anomaly scores
        transactions = self.db.query(Transaction).filter(
            Transaction.org_id == org_id
        ).all()
        
        if not transactions:
            return {"accounts": [], "risk_levels": []}
        
        # Group by account and calculate average risk
        account_risks = {}
        for t in transactions:
            if t.account_id not in account_risks:
                account_risks[t.account_id] = []
            account_risks[t.account_id].append(t.anomaly_score)
        
        # Calculate averages
        heatmap_data = []
        for account_id, scores in account_risks.items():
            avg_score = np.mean(scores)
            heatmap_data.append({
                "account_id": account_id,
                "avg_risk_score": round(avg_score, 3),
                "risk_level": self._score_to_risk_level(avg_score),
                "transaction_count": len(scores)
            })
        
        # Sort by risk score
        heatmap_data.sort(key=lambda x: x["avg_risk_score"], reverse=True)
        
        return {
            "accounts": heatmap_data[:50],  # Top 50 risky accounts
            "total_accounts": len(account_risks)
        }
    
    def calculate_risk_trend(self, org_id: UUID) -> Dict[str, Any]:
        """Calculate week-over-week risk trend"""
        now = datetime.utcnow()
        current_week_start = now - timedelta(days=7)
        previous_week_start = now - timedelta(days=14)
        
        # Current week risk
        current_violations = self.db.query(Violation).filter(
            and_(
                Violation.org_id == org_id,
                Violation.detected_at >= current_week_start
            )
        ).all()
        
        current_avg_risk = np.mean([v.final_risk_score for v in current_violations]) if current_violations else 0
        
        # Previous week risk
        previous_violations = self.db.query(Violation).filter(
            and_(
                Violation.org_id == org_id,
                Violation.detected_at >= previous_week_start,
                Violation.detected_at < current_week_start
            )
        ).all()
        
        previous_avg_risk = np.mean([v.final_risk_score for v in previous_violations]) if previous_violations else 0
        
        # Calculate change
        if previous_avg_risk > 0:
            risk_change_percent = ((current_avg_risk - previous_avg_risk) / previous_avg_risk) * 100
        else:
            risk_change_percent = 0
        
        # Determine trend
        if risk_change_percent > 20:
            trend = "increasing"
            alert_message = "⚠️ Compliance Risk Increasing - Immediate attention required"
        elif risk_change_percent < -20:
            trend = "decreasing"
            alert_message = "✅ Compliance Risk Decreasing - Positive trend"
        else:
            trend = "stable"
            alert_message = "➡️ Compliance Risk Stable"
        
        # Save trend
        risk_trend = RiskTrend(
            org_id=org_id,
            week_start=current_week_start,
            week_end=now,
            avg_risk_score=current_avg_risk,
            total_violations=len(current_violations),
            total_anomalies=sum(1 for v in current_violations if v.anomaly_score > 0.75),
            risk_change_percent=risk_change_percent,
            trend_direction=trend
        )
        self.db.add(risk_trend)
        self.db.commit()
        
        return {
            "current_week_avg_risk": round(current_avg_risk, 2),
            "previous_week_avg_risk": round(previous_avg_risk, 2),
            "risk_change_percent": round(risk_change_percent, 2),
            "trend": trend,
            "alert_message": alert_message,
            "current_violations": len(current_violations),
            "previous_violations": len(previous_violations)
        }
    
    def get_risk_trends_history(self, org_id: UUID, weeks: int = 12) -> List[Dict[str, Any]]:
        """Get historical risk trends"""
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
        
        trends = self.db.query(RiskTrend).filter(
            and_(
                RiskTrend.org_id == org_id,
                RiskTrend.week_start >= cutoff_date
            )
        ).order_by(RiskTrend.week_start.asc()).all()
        
        return [
            {
                "week_start": t.week_start.isoformat(),
                "avg_risk_score": t.avg_risk_score,
                "total_violations": t.total_violations,
                "total_anomalies": t.total_anomalies,
                "risk_change_percent": t.risk_change_percent,
                "trend_direction": t.trend_direction
            }
            for t in trends
        ]
