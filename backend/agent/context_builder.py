"""
Context Builder - Fetches real data from database
CRITICAL: Never let LLM guess numbers
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from uuid import UUID

from app.models.db_models import (
    User, Violation, Policy, Rule, RemediationCase, ScanHistory,
    ViolationStatus, RemediationStatus, PolicyStatus, RuleStatus,
    UserRole, RiskTrend, Transaction
)
from agent.prompts import get_risk_level


class ContextBuilder:
    """Builds structured context from database for AI agent"""
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.org_id = user.org_id
        self.is_restricted = user.role == UserRole.VIEWER
    
    def build_risk_context(self) -> Dict[str, Any]:
        """Build context for risk inquiry"""
        # Get violation counts
        total_violations = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.status == ViolationStatus.PENDING
        ).scalar() or 0
        
        critical = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.severity == "critical",
            Violation.status == ViolationStatus.PENDING
        ).scalar() or 0
        
        high = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.severity == "high",
            Violation.status == ViolationStatus.PENDING
        ).scalar() or 0
        
        medium = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.severity == "medium",
            Violation.status == ViolationStatus.PENDING
        ).scalar() or 0
        
        low = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.severity == "low",
            Violation.status == ViolationStatus.PENDING
        ).scalar() or 0
        
        # Recurring violations (detected more than once)
        recurring = self.db.query(func.count(Violation.violation_id)).filter(
            Violation.org_id == self.org_id,
            Violation.status == ViolationStatus.PENDING,
            Violation.final_risk_score > 0.7
        ).scalar() or 0
        
        # Remediation cases
        open_cases = self.db.query(func.count(RemediationCase.case_id)).filter(
            RemediationCase.org_id == self.org_id,
            RemediationCase.status.in_([RemediationStatus.OPEN, RemediationStatus.IN_PROGRESS])
        ).scalar() or 0
        
        overdue_cases = self.db.query(func.count(RemediationCase.case_id)).filter(
            RemediationCase.org_id == self.org_id,
            RemediationCase.status == RemediationStatus.OVERDUE
        ).scalar() or 0
        
        # Last scan
        last_scan = self.db.query(ScanHistory).filter(
            ScanHistory.org_id == self.org_id
        ).order_by(desc(ScanHistory.scan_date)).first()
        
        last_scan_time = last_scan.scan_date.strftime("%I:%M %p, %b %d") if last_scan else "No scans yet"
        
        # Active policies and rules
        active_policies = self.db.query(func.count(Policy.policy_id)).filter(
            Policy.org_id == self.org_id,
            Policy.status == PolicyStatus.ACTIVE
        ).scalar() or 0
        
        active_rules = self.db.query(func.count(Rule.rule_id)).filter(
            Rule.org_id == self.org_id,
            Rule.status == RuleStatus.ACTIVE
        ).scalar() or 0
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(critical, high, medium, low, total_violations)
        
        # Risk trend
        latest_trend = self.db.query(RiskTrend).filter(
            RiskTrend.org_id == self.org_id
        ).order_by(desc(RiskTrend.week_start)).first()
        
        risk_trend = latest_trend.trend_direction if latest_trend else "stable"
        
        return {
            "risk_score": risk_score,
            "risk_level": get_risk_level(risk_score),
            "risk_trend": risk_trend,
            "total_violations": total_violations,
            "critical_violations": critical,
            "high_violations": high,
            "medium_violations": medium,
            "low_violations": low,
            "recurring_violations": recurring,
            "open_cases": open_cases,
            "overdue_cases": overdue_cases,
            "last_scan_time": last_scan_time,
            "active_policies": active_policies,
            "active_rules": active_rules,
        }
    
    def build_violation_context(self, query: str) -> Dict[str, Any]:
        """Build context for a specific violation query"""
        # Try to extract violation ID or record ID from query
        import re
        
        # Match patterns like TX-234, violation 123, #456
        id_match = re.search(r'(?:TX-?|violation\s*#?|#)(\w+[-]?\w*)', query, re.IGNORECASE)
        
        violation = None
        if id_match:
            search_id = id_match.group(1)
            # Search by record_id first
            violation = self.db.query(Violation).filter(
                Violation.org_id == self.org_id,
                Violation.record_id.ilike(f"%{search_id}%")
            ).first()
            
            # Fallback: search by violation_id
            if not violation:
                try:
                    violation = self.db.query(Violation).filter(
                        Violation.org_id == self.org_id,
                        Violation.violation_id == search_id
                    ).first()
                except Exception:
                    pass
        
        if not violation:
            # Get most recent violation as context
            violation = self.db.query(Violation).filter(
                Violation.org_id == self.org_id
            ).order_by(desc(Violation.detected_at)).first()
        
        if not violation:
            return {"error": "No violations found matching your query."}
        
        # Get related policy and rule
        policy = self.db.query(Policy).filter(Policy.policy_id == violation.policy_id).first()
        rule = self.db.query(Rule).filter(Rule.rule_id == violation.rule_id).first()
        
        context = {
            "violation_id": str(violation.violation_id),
            "severity": violation.severity or "unknown",
            "status": violation.status.value if violation.status else "unknown",
            "detected_at": violation.detected_at.strftime("%Y-%m-%d %H:%M") if violation.detected_at else "unknown",
            "explanation_text": violation.explanation or "No explanation available",
            "field_evaluated": violation.field_name or "N/A",
            "actual_value": violation.field_value or "N/A",
            "expected_condition": rule.rule_text if rule else "N/A",
            "policy_reference": f"{policy.policy_name} v{policy.version}" if policy else "N/A",
            "risk_score": violation.final_risk_score or 0,
            "is_recurring": violation.final_risk_score > 0.7 if violation.final_risk_score else False,
            "occurrence_count": 1,
            "evidence": str(violation.evidence) if violation.evidence else "None",
        }
        
        # Filter financial details for Viewer role
        if self.is_restricted:
            if "amount" in str(context.get("actual_value", "")).lower():
                context["actual_value"] = "[Restricted — Contact admin for financial details]"
        
        return context
    
    def build_policy_context(self, query: str) -> Dict[str, Any]:
        """Build context for policy clarification"""
        # Search for policy by name
        policy = self.db.query(Policy).filter(
            Policy.org_id == self.org_id,
            Policy.policy_name.ilike(f"%{query}%")
        ).first()
        
        if not policy:
            # Get first active policy
            policy = self.db.query(Policy).filter(
                Policy.org_id == self.org_id,
                Policy.status == PolicyStatus.ACTIVE
            ).first()
        
        if not policy:
            return {"error": "No policies found."}
        
        # Count rules for this policy
        rule_count = self.db.query(func.count(Rule.rule_id)).filter(
            Rule.policy_id == policy.policy_id,
            Rule.status == RuleStatus.ACTIVE
        ).scalar() or 0
        
        return {
            "policy_name": policy.policy_name,
            "version": policy.version or "1.0",
            "department": policy.department or "General",
            "framework": policy.regulatory_framework or "N/A",
            "status": policy.status.value if policy.status else "unknown",
            "rule_count": rule_count,
            "uploaded_at": policy.uploaded_at.strftime("%Y-%m-%d") if policy.uploaded_at else "unknown",
            "description": policy.translated_text[:500] if policy.translated_text else "No description available",
        }
    
    def build_remediation_context(self) -> Dict[str, Any]:
        """Build context for remediation status"""
        base_query = self.db.query(RemediationCase).filter(
            RemediationCase.org_id == self.org_id
        )
        
        total = base_query.count()
        open_count = base_query.filter(RemediationCase.status == RemediationStatus.OPEN).count()
        in_progress = base_query.filter(RemediationCase.status == RemediationStatus.IN_PROGRESS).count()
        escalated = base_query.filter(RemediationCase.status == RemediationStatus.ESCALATED).count()
        overdue = base_query.filter(RemediationCase.status == RemediationStatus.OVERDUE).count()
        completed = base_query.filter(RemediationCase.status == RemediationStatus.COMPLETED).count()
        
        # Critical pending
        critical_pending = self.db.query(func.count(RemediationCase.case_id)).filter(
            RemediationCase.org_id == self.org_id,
            RemediationCase.priority == "critical",
            RemediationCase.status.in_([RemediationStatus.OPEN, RemediationStatus.IN_PROGRESS])
        ).scalar() or 0
        
        completion_rate = round((completed / total * 100), 1) if total > 0 else 0
        
        # Recent cases
        recent = self.db.query(RemediationCase).filter(
            RemediationCase.org_id == self.org_id
        ).order_by(desc(RemediationCase.created_at)).limit(5).all()
        
        recent_cases_text = ""
        for case in recent:
            recent_cases_text += (
                f"- Case {str(case.case_id)[:8]}: "
                f"Priority={case.priority.value if case.priority else 'N/A'}, "
                f"Status={case.status.value if case.status else 'N/A'}, "
                f"Due={case.due_date.strftime('%Y-%m-%d') if case.due_date else 'N/A'}\n"
            )
        
        return {
            "total_cases": total,
            "open_cases": open_count,
            "in_progress": in_progress,
            "escalated": escalated,
            "overdue": overdue,
            "completed": completed,
            "critical_pending": critical_pending,
            "completion_rate": completion_rate,
            "recent_cases": recent_cases_text or "No recent cases",
        }
    
    def build_trend_context(self) -> Dict[str, Any]:
        """Build context for trend summary"""
        trends = self.db.query(RiskTrend).filter(
            RiskTrend.org_id == self.org_id
        ).order_by(desc(RiskTrend.week_start)).limit(2).all()
        
        if not trends:
            return {
                "current_risk": 0,
                "previous_risk": 0,
                "risk_change": "0",
                "trend_direction": "No data available",
                "current_violations": 0,
                "previous_violations": 0,
                "new_violations": 0,
                "recurring_violations": 0,
                "time_period": "N/A",
            }
        
        current = trends[0]
        previous = trends[1] if len(trends) > 1 else current
        
        risk_change = current.avg_risk_score - previous.avg_risk_score
        
        return {
            "current_risk": round(current.avg_risk_score, 1),
            "previous_risk": round(previous.avg_risk_score, 1),
            "risk_change": f"{'+' if risk_change > 0 else ''}{round(risk_change, 1)}",
            "trend_direction": current.trend_direction or "stable",
            "current_violations": current.total_violations,
            "previous_violations": previous.total_violations,
            "new_violations": max(0, current.total_violations - previous.total_violations),
            "recurring_violations": current.total_anomalies,
            "time_period": f"{current.week_start.strftime('%b %d')} - {current.week_end.strftime('%b %d')}",
        }
    
    def build_audit_context(self) -> Dict[str, Any]:
        """Build context for audit summary (latest scan)"""
        last_scan = self.db.query(ScanHistory).filter(
            ScanHistory.org_id == self.org_id
        ).order_by(desc(ScanHistory.scan_date)).first()
        
        if not last_scan:
            return {"error": "No scan history available."}
        
        # Get violations from the scan period
        scan_violations = self.db.query(Violation).filter(
            Violation.org_id == self.org_id,
            Violation.detected_at >= last_scan.scan_date - timedelta(hours=1),
            Violation.detected_at <= last_scan.scan_date + timedelta(hours=1)
        ).all()
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in scan_violations:
            if v.severity in severity_counts:
                severity_counts[v.severity] += 1
        
        total_detected = len(scan_violations)
        risk_score = self._calculate_risk_score(
            severity_counts["critical"], severity_counts["high"],
            severity_counts["medium"], severity_counts["low"],
            total_detected
        )
        
        return {
            "scan_id": str(last_scan.scan_id)[:8],
            "scan_date": last_scan.scan_date.strftime("%Y-%m-%d %H:%M"),
            "duration": last_scan.duration_seconds or 0,
            "records_processed": last_scan.records_processed or 0,
            "policies_scanned": last_scan.policies_scanned or 0,
            "rules_executed": last_scan.rules_executed or 0,
            "violations_detected": total_detected,
            "critical_violations": severity_counts["critical"],
            "high_violations": severity_counts["high"],
            "medium_violations": severity_counts["medium"],
            "low_violations": severity_counts["low"],
            "risk_score": risk_score,
            "status": last_scan.status or "completed",
        }
    
    def build_general_context(self) -> Dict[str, Any]:
        """Build general context for general_help intent"""
        risk_context = self.build_risk_context()
        return {
            "risk_score": risk_context["risk_score"],
            "risk_level": risk_context["risk_level"],
            "total_violations": risk_context["total_violations"],
            "critical_violations": risk_context["critical_violations"],
            "open_cases": risk_context["open_cases"],
            "active_policies": risk_context["active_policies"],
        }
    
    def get_sources(self, intent: str, context_data: Dict) -> List[Dict[str, str]]:
        """Generate source references for the response"""
        sources = []
        
        if intent == "violation_explanation" and "violation_id" in context_data:
            sources.append({
                "type": "violation",
                "id": context_data["violation_id"],
                "label": f"Violation {context_data['violation_id'][:8]}"
            })
            if "policy_reference" in context_data:
                sources.append({
                    "type": "policy",
                    "id": "",
                    "label": context_data["policy_reference"]
                })
        elif intent == "risk_inquiry":
            sources.append({
                "type": "system",
                "id": "",
                "label": f"Risk Dashboard (Score: {context_data.get('risk_score', 'N/A')})"
            })
        elif intent == "audit_summary" and "scan_id" in context_data:
            sources.append({
                "type": "scan",
                "id": context_data["scan_id"],
                "label": f"Scan {context_data['scan_id']}"
            })
        
        return sources
    
    def _calculate_risk_score(self, critical: int, high: int, medium: int, low: int, total: int) -> int:
        """Calculate risk score from violation counts"""
        if total == 0:
            return 0
        
        weighted = (critical * 25) + (high * 15) + (medium * 8) + (low * 3)
        score = min(100, weighted)
        return score