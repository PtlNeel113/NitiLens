"""
Enhanced multi-policy compliance scanning engine
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd
from datetime import datetime
from uuid import UUID

from app.models.db_models import Policy, Rule, Violation, PolicyStatus, RuleStatus, ViolationStatus
from app.services.alert_service import alert_service
from app.connectors import create_connector


class ComplianceEngine:
    """Multi-policy compliance scanning engine"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def scan_all_policies(
        self,
        org_id: UUID,
        connector_id: Optional[UUID] = None,
        department: Optional[str] = None,
        framework: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Scan data against all active policies"""
        # Get active policies with filters
        query = self.db.query(Policy).filter(
            and_(
                Policy.org_id == org_id,
                Policy.status == PolicyStatus.ACTIVE
            )
        )
        
        if department:
            query = query.filter(Policy.department == department)
        if framework:
            query = query.filter(Policy.regulatory_framework == framework)
        
        policies = query.all()
        
        if not policies:
            return {
                "status": "error",
                "message": "No active policies found"
            }
        
        # Fetch data from connector
        data = await self._fetch_data(org_id, connector_id, limit)
        
        # Scan each policy
        results = {
            "total_policies": len(policies),
            "total_records": len(data),
            "policies_scanned": [],
            "total_violations": 0,
            "violations_by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        for policy in policies:
            policy_result = await self._scan_policy(policy, data, org_id)
            results["policies_scanned"].append(policy_result)
            results["total_violations"] += policy_result["violations_found"]
            
            # Aggregate severity counts
            for severity, count in policy_result["violations_by_severity"].items():
                results["violations_by_severity"][severity] += count
        
        return results
    
    async def _scan_policy(self, policy: Policy, data: pd.DataFrame, org_id: UUID) -> Dict[str, Any]:
        """Scan data against a single policy"""
        # Get active rules for policy
        rules = self.db.query(Rule).filter(
            and_(
                Rule.policy_id == policy.policy_id,
                Rule.status == RuleStatus.ACTIVE
            )
        ).all()
        
        violations_found = 0
        violations_by_severity = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        # Execute each rule
        for rule in rules:
            rule_violations = await self._execute_rule(rule, data, policy, org_id)
            violations_found += len(rule_violations)
            
            for violation in rule_violations:
                violations_by_severity[violation.severity] += 1
        
        return {
            "policy_id": str(policy.policy_id),
            "policy_name": policy.policy_name,
            "version": policy.version,
            "department": policy.department,
            "framework": policy.regulatory_framework,
            "rules_executed": len(rules),
            "violations_found": violations_found,
            "violations_by_severity": violations_by_severity
        }
    
    async def _execute_rule(
        self,
        rule: Rule,
        data: pd.DataFrame,
        policy: Policy,
        org_id: UUID
    ) -> List[Violation]:
        """Execute a single rule against data"""
        violations = []
        
        try:
            # Parse structured logic
            logic = rule.structured_logic or {}
            
            # Execute rule based on logic type
            if logic.get("type") == "threshold":
                violations = self._check_threshold(rule, data, policy, org_id, logic)
            elif logic.get("type") == "pattern":
                violations = self._check_pattern(rule, data, policy, org_id, logic)
            elif logic.get("type") == "comparison":
                violations = self._check_comparison(rule, data, policy, org_id, logic)
            else:
                # Default: check rule text against data
                violations = self._check_generic(rule, data, policy, org_id)
            
            # Import anomaly detector and remediation engine
            from app.services.anomaly_detector import AnomalyDetector
            from app.services.remediation_engine import RemediationEngine
            
            detector = AnomalyDetector(self.db)
            remediation = RemediationEngine(self.db)
            
            # Save violations and create remediation cases
            for violation in violations:
                # Calculate combined risk score
                anomaly_score = violation.anomaly_score if hasattr(violation, 'anomaly_score') else 0.0
                violation.final_risk_score = detector.calculate_combined_risk_score(
                    violation.severity,
                    anomaly_score
                )
                
                self.db.add(violation)
                self.db.flush()
                
                # Create remediation case automatically
                await remediation.create_remediation_case(violation)
                
                # Send real-time alerts for high/critical violations
                if violation.severity in ["high", "critical"]:
                    await alert_service.send_alert(
                        self.db,
                        violation,
                        channels=["websocket", "email"],
                        recipients={"email": "compliance@example.com"}
                    )
            
            self.db.commit()
            
        except Exception as e:
            print(f"Rule execution error: {e}")
        
        return violations
    
    def _check_threshold(
        self,
        rule: Rule,
        data: pd.DataFrame,
        policy: Policy,
        org_id: UUID,
        logic: Dict
    ) -> List[Violation]:
        """Check threshold-based rules"""
        violations = []
        field = logic.get("field")
        threshold = logic.get("threshold")
        operator = logic.get("operator", ">")
        
        if field not in data.columns:
            return violations
        
        # Apply threshold check
        if operator == ">":
            mask = data[field] > threshold
        elif operator == "<":
            mask = data[field] < threshold
        elif operator == ">=":
            mask = data[field] >= threshold
        elif operator == "<=":
            mask = data[field] <= threshold
        elif operator == "==":
            mask = data[field] == threshold
        else:
            return violations
        
        violating_records = data[mask]
        
        for _, record in violating_records.iterrows():
            violation = Violation(
                rule_id=rule.rule_id,
                policy_id=policy.policy_id,
                org_id=org_id,
                department=policy.department,
                severity=rule.severity,
                record_id=str(record.get("transaction_id", "")),
                field_name=field,
                field_value=str(record[field]),
                explanation=f"Value {record[field]} violates threshold {operator} {threshold}",
                evidence=record.to_dict(),
                status=ViolationStatus.PENDING
            )
            violations.append(violation)
        
        return violations
    
    def _check_pattern(
        self,
        rule: Rule,
        data: pd.DataFrame,
        policy: Policy,
        org_id: UUID,
        logic: Dict
    ) -> List[Violation]:
        """Check pattern-based rules"""
        violations = []
        field = logic.get("field")
        pattern = logic.get("pattern")
        
        if field not in data.columns:
            return violations
        
        # Check pattern match
        mask = data[field].astype(str).str.contains(pattern, case=False, na=False)
        violating_records = data[mask]
        
        for _, record in violating_records.iterrows():
            violation = Violation(
                rule_id=rule.rule_id,
                policy_id=policy.policy_id,
                org_id=org_id,
                department=policy.department,
                severity=rule.severity,
                record_id=str(record.get("transaction_id", "")),
                field_name=field,
                field_value=str(record[field]),
                explanation=f"Value matches prohibited pattern: {pattern}",
                evidence=record.to_dict(),
                status=ViolationStatus.PENDING
            )
            violations.append(violation)
        
        return violations
    
    def _check_comparison(
        self,
        rule: Rule,
        data: pd.DataFrame,
        policy: Policy,
        org_id: UUID,
        logic: Dict
    ) -> List[Violation]:
        """Check comparison-based rules"""
        violations = []
        field1 = logic.get("field1")
        field2 = logic.get("field2")
        operator = logic.get("operator", ">")
        
        if field1 not in data.columns or field2 not in data.columns:
            return violations
        
        # Apply comparison
        if operator == ">":
            mask = data[field1] > data[field2]
        elif operator == "<":
            mask = data[field1] < data[field2]
        elif operator == "==":
            mask = data[field1] == data[field2]
        else:
            return violations
        
        violating_records = data[mask]
        
        for _, record in violating_records.iterrows():
            violation = Violation(
                rule_id=rule.rule_id,
                policy_id=policy.policy_id,
                org_id=org_id,
                department=policy.department,
                severity=rule.severity,
                record_id=str(record.get("transaction_id", "")),
                field_name=f"{field1} vs {field2}",
                field_value=f"{record[field1]} vs {record[field2]}",
                explanation=f"{field1} ({record[field1]}) {operator} {field2} ({record[field2]})",
                evidence=record.to_dict(),
                status=ViolationStatus.PENDING
            )
            violations.append(violation)
        
        return violations
    
    def _check_generic(
        self,
        rule: Rule,
        data: pd.DataFrame,
        policy: Policy,
        org_id: UUID
    ) -> List[Violation]:
        """Generic rule checking (fallback)"""
        # Simplified generic check - can be enhanced with NLP
        return []
    
    async def _fetch_data(
        self,
        org_id: UUID,
        connector_id: Optional[UUID],
        limit: Optional[int]
    ) -> pd.DataFrame:
        """Fetch data from connector or default source"""
        if connector_id:
            from app.models.db_models import Connector
            connector = self.db.query(Connector).filter(
                Connector.connector_id == connector_id,
                Connector.org_id == org_id
            ).first()
            
            if connector:
                from app.connectors import create_connector
                conn = create_connector(
                    connector.connector_type.value,
                    connector.connection_config,
                    connector.field_mapping
                )
                return conn.fetch_data(limit=limit)
        
        # Default: load sample data
        return pd.read_csv("data/datasets/ibm_aml/sample_transactions.csv", nrows=limit)
