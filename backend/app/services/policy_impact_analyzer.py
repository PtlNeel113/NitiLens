"""
Policy Change Impact Analysis
Automatically detect and measure impact when policy versions change
"""
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID
import json

from app.models.db_models import (
    Policy, Rule, Violation, PolicyChangeLog, ChangeType, RuleStatus
)


class PolicyImpactAnalyzer:
    """Analyzes impact of policy changes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def analyze_policy_update(self, old_policy_id: UUID, new_policy_id: UUID) -> Dict[str, Any]:
        """
        Compare old and new policy versions
        Detect rule changes and measure impact
        """
        old_policy = self.db.query(Policy).filter(Policy.policy_id == old_policy_id).first()
        new_policy = self.db.query(Policy).filter(Policy.policy_id == new_policy_id).first()
        
        if not old_policy or not new_policy:
            raise ValueError("Policy not found")
        
        # Get rules for both versions
        old_rules = self.db.query(Rule).filter(
            and_(
                Rule.policy_id == old_policy_id,
                Rule.is_active == True
            )
        ).all()
        
        new_rules = self.db.query(Rule).filter(
            and_(
                Rule.policy_id == new_policy_id,
                Rule.is_active == True
            )
        ).all()
        
        # Detect changes
        changes = self._detect_rule_changes(old_rules, new_rules)
        
        # Log changes
        change_logs = []
        for change in changes:
            log = PolicyChangeLog(
                policy_id=new_policy_id,
                old_rule_id=change.get("old_rule_id"),
                new_rule_id=change.get("new_rule_id"),
                change_type=change["type"],
                change_details=change["details"]
            )
            self.db.add(log)
            change_logs.append(log)
        
        self.db.commit()
        
        # Calculate impact for modified and new rules
        impact_summary = self._calculate_impact(changes, new_policy.org_id)
        
        # Update change logs with impact data
        for log in change_logs:
            if log.change_type in [ChangeType.MODIFIED, ChangeType.NEW]:
                rule_impact = next(
                    (i for i in impact_summary["rule_impacts"] 
                     if i.get("new_rule_id") == str(log.new_rule_id)),
                    None
                )
                if rule_impact:
                    log.old_violations_count = rule_impact.get("old_violations", 0)
                    log.new_violations_count = rule_impact.get("new_violations", 0)
                    log.net_risk_delta = rule_impact.get("risk_delta", 0.0)
        
        self.db.commit()
        
        return {
            "policy_name": new_policy.policy_name,
            "old_version": old_policy.version,
            "new_version": new_policy.version,
            "changes": changes,
            "impact": impact_summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _detect_rule_changes(self, old_rules: List[Rule], new_rules: List[Rule]) -> List[Dict[str, Any]]:
        """Detect differences between old and new rule sets"""
        changes = []
        
        # Create lookup maps
        old_rules_map = {self._rule_signature(r): r for r in old_rules}
        new_rules_map = {self._rule_signature(r): r for r in new_rules}
        
        # Find modified and removed rules
        for signature, old_rule in old_rules_map.items():
            if signature in new_rules_map:
                new_rule = new_rules_map[signature]
                # Check if logic changed
                if self._has_logic_changed(old_rule, new_rule):
                    changes.append({
                        "type": ChangeType.MODIFIED,
                        "old_rule_id": old_rule.rule_id,
                        "new_rule_id": new_rule.rule_id,
                        "details": self._get_change_details(old_rule, new_rule)
                    })
                    # Link rules for versioning
                    new_rule.previous_rule_id = old_rule.rule_id
            else:
                changes.append({
                    "type": ChangeType.REMOVED,
                    "old_rule_id": old_rule.rule_id,
                    "new_rule_id": None,
                    "details": {
                        "rule_text": old_rule.rule_text,
                        "severity": old_rule.severity
                    }
                })
                # Deactivate old rule
                old_rule.is_active = False
        
        # Find new rules
        for signature, new_rule in new_rules_map.items():
            if signature not in old_rules_map:
                changes.append({
                    "type": ChangeType.NEW,
                    "old_rule_id": None,
                    "new_rule_id": new_rule.rule_id,
                    "details": {
                        "rule_text": new_rule.rule_text,
                        "severity": new_rule.severity,
                        "logic": new_rule.structured_logic
                    }
                })
        
        return changes
    
    def _rule_signature(self, rule: Rule) -> str:
        """Generate signature for rule matching"""
        logic = rule.structured_logic or {}
        field = logic.get("field", "")
        rule_type = logic.get("type", "")
        return f"{rule_type}:{field}:{rule.rule_text[:50]}"
    
    def _has_logic_changed(self, old_rule: Rule, new_rule: Rule) -> bool:
        """Check if rule logic has changed"""
        old_logic = old_rule.structured_logic or {}
        new_logic = new_rule.structured_logic or {}
        
        # Check if threshold changed
        if old_logic.get("threshold") != new_logic.get("threshold"):
            return True
        
        # Check if operator changed
        if old_logic.get("operator") != new_logic.get("operator"):
            return True
        
        # Check if pattern changed
        if old_logic.get("pattern") != new_logic.get("pattern"):
            return True
        
        # Check if severity changed
        if old_rule.severity != new_rule.severity:
            return True
        
        return False
    
    def _get_change_details(self, old_rule: Rule, new_rule: Rule) -> Dict[str, Any]:
        """Get detailed change information"""
        old_logic = old_rule.structured_logic or {}
        new_logic = new_rule.structured_logic or {}
        
        details = {
            "rule_text": new_rule.rule_text,
            "changes": []
        }
        
        # Threshold change
        if old_logic.get("threshold") != new_logic.get("threshold"):
            details["changes"].append({
                "field": "threshold",
                "old_value": old_logic.get("threshold"),
                "new_value": new_logic.get("threshold"),
                "impact": "stricter" if new_logic.get("threshold", 0) < old_logic.get("threshold", 0) else "relaxed"
            })
        
        # Operator change
        if old_logic.get("operator") != new_logic.get("operator"):
            details["changes"].append({
                "field": "operator",
                "old_value": old_logic.get("operator"),
                "new_value": new_logic.get("operator")
            })
        
        # Severity change
        if old_rule.severity != new_rule.severity:
            details["changes"].append({
                "field": "severity",
                "old_value": old_rule.severity,
                "new_value": new_rule.severity
            })
        
        return details
    
    def _calculate_impact(self, changes: List[Dict[str, Any]], org_id: UUID) -> Dict[str, Any]:
        """Calculate impact of policy changes"""
        total_new_violations = 0
        total_resolved_violations = 0
        rule_impacts = []
        
        for change in changes:
            if change["type"] == ChangeType.MODIFIED:
                old_rule_id = change["old_rule_id"]
                new_rule_id = change["new_rule_id"]
                
                # Count old violations
                old_violations = self.db.query(Violation).filter(
                    and_(
                        Violation.rule_id == old_rule_id,
                        Violation.org_id == org_id
                    )
                ).count()
                
                # For modified rules, estimate impact based on threshold change
                details = change["details"]
                threshold_change = next(
                    (c for c in details.get("changes", []) if c["field"] == "threshold"),
                    None
                )
                
                if threshold_change:
                    impact = threshold_change.get("impact", "unknown")
                    if impact == "stricter":
                        # Stricter rules = more violations
                        estimated_new = int(old_violations * 1.3)  # 30% increase estimate
                        new_violations = estimated_new - old_violations
                        total_new_violations += new_violations
                    else:
                        # Relaxed rules = fewer violations
                        estimated_new = int(old_violations * 0.7)  # 30% decrease estimate
                        resolved = old_violations - estimated_new
                        total_resolved_violations += resolved
                    
                    rule_impacts.append({
                        "rule_id": str(new_rule_id),
                        "new_rule_id": str(new_rule_id),
                        "old_violations": old_violations,
                        "new_violations": estimated_new,
                        "risk_delta": estimated_new - old_violations,
                        "change_type": "modified",
                        "threshold_change": threshold_change
                    })
            
            elif change["type"] == ChangeType.NEW:
                # New rules will detect new violations
                # Estimate based on average violations per rule
                avg_violations = self._get_average_violations_per_rule(org_id)
                total_new_violations += avg_violations
                
                rule_impacts.append({
                    "rule_id": str(change["new_rule_id"]),
                    "new_rule_id": str(change["new_rule_id"]),
                    "old_violations": 0,
                    "new_violations": avg_violations,
                    "risk_delta": avg_violations,
                    "change_type": "new"
                })
            
            elif change["type"] == ChangeType.REMOVED:
                # Removed rules = violations no longer detected
                old_rule_id = change["old_rule_id"]
                old_violations = self.db.query(Violation).filter(
                    and_(
                        Violation.rule_id == old_rule_id,
                        Violation.org_id == org_id
                    )
                ).count()
                
                total_resolved_violations += old_violations
                
                rule_impacts.append({
                    "rule_id": str(old_rule_id),
                    "old_rule_id": str(old_rule_id),
                    "old_violations": old_violations,
                    "new_violations": 0,
                    "risk_delta": -old_violations,
                    "change_type": "removed"
                })
        
        net_risk_delta = total_new_violations - total_resolved_violations
        risk_change_percent = 0
        
        if total_resolved_violations > 0:
            risk_change_percent = round(
                (net_risk_delta / total_resolved_violations) * 100, 2
            )
        
        return {
            "new_violations": total_new_violations,
            "resolved_violations": total_resolved_violations,
            "net_risk_delta": net_risk_delta,
            "risk_change_percent": risk_change_percent,
            "risk_direction": "increased" if net_risk_delta > 0 else "decreased" if net_risk_delta < 0 else "stable",
            "rule_impacts": rule_impacts
        }
    
    def _get_average_violations_per_rule(self, org_id: UUID) -> int:
        """Calculate average violations per rule for estimation"""
        total_violations = self.db.query(Violation).filter(
            Violation.org_id == org_id
        ).count()
        
        total_rules = self.db.query(Rule).filter(
            and_(
                Rule.org_id == org_id,
                Rule.is_active == True
            )
        ).count()
        
        if total_rules == 0:
            return 10  # Default estimate
        
        return int(total_violations / total_rules)
    
    def get_policy_history(self, policy_id: UUID) -> List[Dict[str, Any]]:
        """Get change history for a policy"""
        changes = self.db.query(PolicyChangeLog).filter(
            PolicyChangeLog.policy_id == policy_id
        ).order_by(PolicyChangeLog.detected_at.desc()).all()
        
        return [
            {
                "change_id": str(c.change_id),
                "change_type": c.change_type.value,
                "old_violations": c.old_violations_count,
                "new_violations": c.new_violations_count,
                "net_risk_delta": c.net_risk_delta,
                "detected_at": c.detected_at.isoformat(),
                "details": c.change_details
            }
            for c in changes
        ]
