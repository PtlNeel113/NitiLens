"""
Automated Remediation Engine
Full lifecycle management from violation detection to resolution tracking
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from uuid import UUID
import uuid

from app.models.db_models import (
    RemediationCase, RemediationComment, Violation, Rule, User,
    RemediationStatus, RemediationPriority, UserRole
)
from app.services.alert_service import alert_service


class RemediationEngine:
    """Manages automated remediation workflow"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_remediation_case(self, violation: Violation) -> RemediationCase:
        """
        Auto-create remediation case when violation is detected
        Includes auto-recommendation and auto-assignment
        """
        # Get rule details
        rule = self.db.query(Rule).filter(Rule.rule_id == violation.rule_id).first()
        
        # Generate recommended action based on rule type
        recommended_action = self._generate_recommendation(rule, violation)
        
        # Determine priority from severity
        priority = self._severity_to_priority(violation.severity)
        
        # Calculate due date based on priority
        due_date = self._calculate_due_date(priority)
        
        # Auto-assign to appropriate user
        assigned_user = self._auto_assign(violation.org_id, priority)
        
        # Create remediation case
        case = RemediationCase(
            violation_id=violation.violation_id,
            rule_id=violation.rule_id,
            org_id=violation.org_id,
            assigned_to=assigned_user.user_id if assigned_user else None,
            status=RemediationStatus.OPEN,
            priority=priority,
            recommended_action=recommended_action,
            due_date=due_date
        )
        
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        
        # Send notification to assigned user
        if assigned_user:
            await alert_service.send_alert(
                self.db,
                violation,
                channels=["email"],
                recipients={"email": assigned_user.email}
            )
        
        return case
    
    def _generate_recommendation(self, rule: Rule, violation: Violation) -> str:
        """Generate recommended action based on rule type and violation"""
        logic = rule.structured_logic or {}
        rule_type = logic.get("type", "generic")
        
        recommendations = {
            "threshold": (
                f"IMMEDIATE ACTION REQUIRED:\n"
                f"1. File regulatory report within 24 hours\n"
                f"2. Notify compliance officer and legal team\n"
                f"3. Document all communications\n"
                f"4. Review transaction history for pattern\n"
                f"5. Prepare explanation for regulatory inquiry\n\n"
                f"Violation Details: {violation.explanation}"
            ),
            "frequency": (
                f"ENHANCED DUE DILIGENCE REQUIRED:\n"
                f"1. Initiate enhanced due diligence (EDD) process\n"
                f"2. Freeze suspicious account pending review\n"
                f"3. Request additional documentation from customer\n"
                f"4. Review all linked accounts and transactions\n"
                f"5. Escalate to AML investigation team if pattern confirmed\n"
                f"6. File SAR if suspicious activity confirmed\n\n"
                f"Violation Details: {violation.explanation}"
            ),
            "pattern": (
                f"IMMEDIATE ESCALATION REQUIRED:\n"
                f"1. Escalate to AML investigation team immediately\n"
                f"2. Review all linked transactions and accounts\n"
                f"3. Identify beneficial owners and related parties\n"
                f"4. Freeze all related accounts pending investigation\n"
                f"5. Prepare Suspicious Activity Report (SAR)\n"
                f"6. Coordinate with law enforcement if necessary\n"
                f"7. Document complete investigation trail\n\n"
                f"Violation Details: {violation.explanation}"
            ),
            "comparison": (
                f"REVIEW AND VERIFICATION REQUIRED:\n"
                f"1. Verify data accuracy and completeness\n"
                f"2. Review business justification\n"
                f"3. Request supporting documentation\n"
                f"4. Assess compliance with internal policies\n"
                f"5. Document findings and resolution\n\n"
                f"Violation Details: {violation.explanation}"
            ),
            "generic": (
                f"COMPLIANCE REVIEW REQUIRED:\n"
                f"1. Review violation details and evidence\n"
                f"2. Assess severity and potential impact\n"
                f"3. Determine appropriate corrective action\n"
                f"4. Document resolution and preventive measures\n"
                f"5. Update compliance procedures if needed\n\n"
                f"Violation Details: {violation.explanation}"
            )
        }
        
        return recommendations.get(rule_type, recommendations["generic"])
    
    def _severity_to_priority(self, severity: str) -> RemediationPriority:
        """Map violation severity to remediation priority"""
        mapping = {
            "critical": RemediationPriority.CRITICAL,
            "high": RemediationPriority.HIGH,
            "medium": RemediationPriority.MEDIUM,
            "low": RemediationPriority.LOW
        }
        return mapping.get(severity.lower(), RemediationPriority.MEDIUM)
    
    def _calculate_due_date(self, priority: RemediationPriority) -> datetime:
        """Calculate due date based on priority"""
        hours_map = {
            RemediationPriority.CRITICAL: 24,   # 1 day
            RemediationPriority.HIGH: 72,       # 3 days
            RemediationPriority.MEDIUM: 168,    # 7 days
            RemediationPriority.LOW: 336        # 14 days
        }
        hours = hours_map.get(priority, 168)
        return datetime.utcnow() + timedelta(hours=hours)
    
    def _auto_assign(self, org_id: UUID, priority: RemediationPriority) -> Optional[User]:
        """Auto-assign case based on priority and user role"""
        role_mapping = {
            RemediationPriority.CRITICAL: [UserRole.SUPER_ADMIN, UserRole.COMPLIANCE_ADMIN],
            RemediationPriority.HIGH: [UserRole.COMPLIANCE_ADMIN, UserRole.REVIEWER],
            RemediationPriority.MEDIUM: [UserRole.REVIEWER],
            RemediationPriority.LOW: [UserRole.REVIEWER, UserRole.VIEWER]
        }
        
        target_roles = role_mapping.get(priority, [UserRole.REVIEWER])
        
        # Find user with least active cases
        users = self.db.query(User).filter(
            and_(
                User.org_id == org_id,
                User.role.in_(target_roles),
                User.is_active == True
            )
        ).all()
        
        if not users:
            # Fallback to any admin
            users = self.db.query(User).filter(
                and_(
                    User.org_id == org_id,
                    User.role == UserRole.COMPLIANCE_ADMIN,
                    User.is_active == True
                )
            ).all()
        
        if not users:
            return None
        
        # Find user with least active cases
        user_case_counts = []
        for user in users:
            active_cases = self.db.query(RemediationCase).filter(
                and_(
                    RemediationCase.assigned_to == user.user_id,
                    RemediationCase.status.in_([
                        RemediationStatus.OPEN,
                        RemediationStatus.IN_PROGRESS,
                        RemediationStatus.ESCALATED
                    ])
                )
            ).count()
            user_case_counts.append((user, active_cases))
        
        # Sort by case count and return user with least cases
        user_case_counts.sort(key=lambda x: x[1])
        return user_case_counts[0][0]
    
    async def check_escalations(self):
        """Check for overdue cases and auto-escalate"""
        now = datetime.utcnow()
        
        # Find overdue cases
        overdue_cases = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.due_date < now,
                RemediationCase.status != RemediationStatus.COMPLETED,
                RemediationCase.status != RemediationStatus.OVERDUE
            )
        ).all()
        
        for case in overdue_cases:
            case.status = RemediationStatus.OVERDUE
            
            # Send escalation alert
            violation = self.db.query(Violation).filter(
                Violation.violation_id == case.violation_id
            ).first()
            
            if violation:
                await alert_service.send_alert(
                    self.db,
                    violation,
                    channels=["email", "slack"],
                    recipients={"email": "compliance-admin@example.com"}
                )
        
        # Find cases overdue > 48 hours - escalate to admin
        escalation_threshold = now - timedelta(hours=48)
        critical_overdue = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.due_date < escalation_threshold,
                RemediationCase.status == RemediationStatus.OVERDUE
            )
        ).all()
        
        for case in critical_overdue:
            # Reassign to compliance admin
            admin = self.db.query(User).filter(
                and_(
                    User.org_id == case.org_id,
                    User.role == UserRole.COMPLIANCE_ADMIN,
                    User.is_active == True
                )
            ).first()
            
            if admin:
                case.assigned_to = admin.user_id
                case.status = RemediationStatus.ESCALATED
                
                # Add system comment
                comment = RemediationComment(
                    case_id=case.case_id,
                    user_id=admin.user_id,
                    comment_text="SYSTEM: Case auto-escalated due to 48+ hours overdue. Requires immediate attention."
                )
                self.db.add(comment)
        
        self.db.commit()
    
    def update_case_status(
        self,
        case_id: UUID,
        status: RemediationStatus,
        user_id: UUID,
        comment: Optional[str] = None
    ) -> RemediationCase:
        """Update case status with optional comment"""
        case = self.db.query(RemediationCase).filter(
            RemediationCase.case_id == case_id
        ).first()
        
        if not case:
            raise ValueError("Case not found")
        
        case.status = status
        case.updated_at = datetime.utcnow()
        
        if status == RemediationStatus.COMPLETED:
            case.completed_at = datetime.utcnow()
        
        if comment:
            case_comment = RemediationComment(
                case_id=case_id,
                user_id=user_id,
                comment_text=comment
            )
            self.db.add(case_comment)
        
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def reassign_case(self, case_id: UUID, new_user_id: UUID, reassigned_by: UUID) -> RemediationCase:
        """Reassign case to different user"""
        case = self.db.query(RemediationCase).filter(
            RemediationCase.case_id == case_id
        ).first()
        
        if not case:
            raise ValueError("Case not found")
        
        old_user = self.db.query(User).filter(User.user_id == case.assigned_to).first()
        new_user = self.db.query(User).filter(User.user_id == new_user_id).first()
        
        case.assigned_to = new_user_id
        case.updated_at = datetime.utcnow()
        
        # Add system comment
        comment = RemediationComment(
            case_id=case_id,
            user_id=reassigned_by,
            comment_text=f"Case reassigned from {old_user.full_name if old_user else 'Unassigned'} to {new_user.full_name if new_user else 'Unknown'}"
        )
        self.db.add(comment)
        
        self.db.commit()
        self.db.refresh(case)
        
        return case
    
    def get_cases(
        self,
        org_id: UUID,
        status: Optional[RemediationStatus] = None,
        priority: Optional[RemediationPriority] = None,
        assigned_to: Optional[UUID] = None
    ) -> List[RemediationCase]:
        """Get remediation cases with filters"""
        query = self.db.query(RemediationCase).filter(
            RemediationCase.org_id == org_id
        )
        
        if status:
            query = query.filter(RemediationCase.status == status)
        if priority:
            query = query.filter(RemediationCase.priority == priority)
        if assigned_to:
            query = query.filter(RemediationCase.assigned_to == assigned_to)
        
        return query.order_by(RemediationCase.due_date.asc()).all()
    
    def get_case_statistics(self, org_id: UUID) -> Dict[str, Any]:
        """Get remediation statistics for organization"""
        total_cases = self.db.query(RemediationCase).filter(
            RemediationCase.org_id == org_id
        ).count()
        
        open_cases = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.status == RemediationStatus.OPEN
            )
        ).count()
        
        in_progress = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.status == RemediationStatus.IN_PROGRESS
            )
        ).count()
        
        escalated = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.status == RemediationStatus.ESCALATED
            )
        ).count()
        
        overdue = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.status == RemediationStatus.OVERDUE
            )
        ).count()
        
        completed = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.status == RemediationStatus.COMPLETED
            )
        ).count()
        
        # Priority breakdown
        critical = self.db.query(RemediationCase).filter(
            and_(
                RemediationCase.org_id == org_id,
                RemediationCase.priority == RemediationPriority.CRITICAL,
                RemediationCase.status != RemediationStatus.COMPLETED
            )
        ).count()
        
        return {
            "total_cases": total_cases,
            "open": open_cases,
            "in_progress": in_progress,
            "escalated": escalated,
            "overdue": overdue,
            "completed": completed,
            "critical_pending": critical,
            "completion_rate": round((completed / total_cases * 100) if total_cases > 0 else 0, 2)
        }
