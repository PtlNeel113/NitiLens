"""
Real-time alert system with WebSocket, Email, and Slack support
"""
import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import httpx
import redis
from sqlalchemy.orm import Session

from app.models.db_models import Alert, Violation, AlertChannel, AlertStatus


class AlertService:
    """Manages real-time alerts across multiple channels"""
    
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        self.sendgrid_key = os.getenv("EMAIL_API_KEY")
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.email_from = os.getenv("EMAIL_FROM", "noreply@nitilens.com")
        self.websocket_connections: Dict[str, List] = {}
    
    async def send_alert(self, db: Session, violation: Violation, channels: List[str], recipients: Dict[str, str]):
        """Send alert through specified channels"""
        tasks = []
        
        for channel in channels:
            if channel == "email" and recipients.get("email"):
                tasks.append(self._send_email_alert(db, violation, recipients["email"]))
            elif channel == "slack" and self.slack_webhook:
                tasks.append(self._send_slack_alert(db, violation))
            elif channel == "websocket":
                tasks.append(self._send_websocket_alert(violation))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_email_alert(self, db: Session, violation: Violation, recipient: str):
        """Send email alert via SendGrid"""
        alert = Alert(
            violation_id=violation.violation_id,
            org_id=violation.org_id,
            channel=AlertChannel.EMAIL,
            recipient=recipient,
            status=AlertStatus.PENDING
        )
        db.add(alert)
        db.commit()
        
        try:
            if not self.sendgrid_key:
                raise ValueError("SendGrid API key not configured")
            
            message = Mail(
                from_email=self.email_from,
                to_emails=recipient,
                subject=f"[{violation.severity.upper()}] Compliance Violation Detected",
                html_content=self._format_email_content(violation)
            )
            
            sg = SendGridAPIClient(self.sendgrid_key)
            response = sg.send(message)
            
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            alert.status = AlertStatus.FAILED
            alert.error_message = str(e)[:500]
            db.commit()
    
    async def _send_slack_alert(self, db: Session, violation: Violation):
        """Send Slack alert via webhook"""
        alert = Alert(
            violation_id=violation.violation_id,
            org_id=violation.org_id,
            channel=AlertChannel.SLACK,
            recipient="slack_channel",
            status=AlertStatus.PENDING
        )
        db.add(alert)
        db.commit()
        
        try:
            if not self.slack_webhook:
                raise ValueError("Slack webhook not configured")
            
            payload = {
                "text": f"🚨 *{violation.severity.upper()} Compliance Violation*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 {violation.severity.upper()} Violation Detected"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Violation ID:*\n{violation.violation_id}"},
                            {"type": "mrkdwn", "text": f"*Severity:*\n{violation.severity}"},
                            {"type": "mrkdwn", "text": f"*Department:*\n{violation.department or 'N/A'}"},
                            {"type": "mrkdwn", "text": f"*Detected:*\n{violation.detected_at.strftime('%Y-%m-%d %H:%M')}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Explanation:*\n{violation.explanation}"
                        }
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.slack_webhook, json=payload, timeout=10)
                response.raise_for_status()
            
            alert.status = AlertStatus.SENT
            alert.sent_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            alert.status = AlertStatus.FAILED
            alert.error_message = str(e)[:500]
            db.commit()
    
    async def _send_websocket_alert(self, violation: Violation):
        """Broadcast alert via WebSocket"""
        try:
            alert_data = {
                "type": "violation_alert",
                "violation_id": str(violation.violation_id),
                "severity": violation.severity,
                "department": violation.department,
                "explanation": violation.explanation,
                "detected_at": violation.detected_at.isoformat()
            }
            
            # Publish to Redis for WebSocket servers
            self.redis_client.publish(
                f"alerts:{violation.org_id}",
                json.dumps(alert_data)
            )
            
        except Exception as e:
            print(f"WebSocket alert failed: {e}")
    
    def _format_email_content(self, violation: Violation) -> str:
        """Format email HTML content"""
        severity_colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#f59e0b",
            "low": "#84cc16"
        }
        
        color = severity_colors.get(violation.severity, "#6b7280")
        
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="border-left: 4px solid {color}; padding-left: 20px;">
                    <h2 style="color: {color};">Compliance Violation Detected</h2>
                    <p><strong>Severity:</strong> {violation.severity.upper()}</p>
                    <p><strong>Department:</strong> {violation.department or 'N/A'}</p>
                    <p><strong>Detected:</strong> {violation.detected_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    <h3>Explanation:</h3>
                    <p>{violation.explanation}</p>
                    <hr>
                    <p style="color: #6b7280; font-size: 12px;">
                        Violation ID: {violation.violation_id}<br>
                        This is an automated alert from NitiLens Compliance Platform
                    </p>
                </div>
            </body>
        </html>
        """


# Global instance
alert_service = AlertService()
