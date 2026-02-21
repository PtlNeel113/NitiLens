"""
End-to-End Test Suite for Enterprise Upgrade
Tests all enterprise features: scan history, review logging, explainability, risk scoring
"""
import pytest
import asyncio
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

from backend.app.models.db_models import (
    Organization, User, Policy, Rule, Violation, ScanHistory, ReviewLog,
    PolicyStatus, RuleStatus, ViolationStatus, UserRole, SubscriptionPlan
)
from backend.app.services.rule_engine import RuleEngine
from backend.app.services.compliance_engine import ComplianceEngine
from backend.app.database import Base


# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql://nitilens:nitilens_password@localhost:5432/nitilens_test_db"


@pytest.fixture(scope="module")
def db_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create database session for each test"""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_org(db_session):
    """Create test organization"""
    org = Organization(
        org_name="Test Organization",
        subscription_plan=SubscriptionPlan.PRO
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_user(db_session, test_org):
    """Create test user"""
    user = User(
        org_id=test_org.org_id,
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        role=UserRole.COMPLIANCE_ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_policy(db_session, test_org):
    """Create test policy"""
    policy = Policy(
        org_id=test_org.org_id,
        policy_name="AML Policy",
        version="2.1",
        department="Compliance",
        regulatory_framework="AML",
        status=PolicyStatus.ACTIVE
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


@pytest.fixture
def test_rule(db_session, test_org, test_policy):
    """Create test rule with structured logic"""
    rule = Rule(
        policy_id=test_policy.policy_id,
        org_id=test_org.org_id,
        rule_text="Large transactions over $10,000",
        structured_logic={
            "conditions": [
                {
                    "field": "Amount Paid",
                    "operator": ">",
                    "value": 10000,
                    "logical_group": "A"
                }
            ],
            "logical_operator": "AND"
        },
        severity="high",
        status=RuleStatus.ACTIVE
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def test_data():
    """Create test transaction data"""
    return pd.DataFrame([
        {
            "transaction_id": "TXN001",
            "Amount Paid": 15000,
            "Payment Currency": "USD",
            "Receiving Currency": "USD",
            "Account": "ACC001",
            "Account.1": "ACC002"
        },
        {
            "transaction_id": "TXN002",
            "Amount Paid": 5000,
            "Payment Currency": "USD",
            "Receiving Currency": "USD",
            "Account": "ACC003",
            "Account.1": "ACC004"
        },
        {
            "transaction_id": "TXN003",
            "Amount Paid": 25000,
            "Payment Currency": "USD",
            "Receiving Currency": "EUR",
            "Account": "ACC005",
            "Account.1": "ACC006"
        }
    ])


class TestRuleEngine:
    """Test dynamic rule engine"""
    
    def test_rule_validation(self):
        """Test rule structure validation"""
        engine = RuleEngine()
        
        # Valid rule
        valid_rule = {
            "rule_id": str(uuid4()),
            "conditions": [
                {
                    "field": "amount",
                    "operator": ">",
                    "value": 10000,
                    "logical_group": "A"
                }
            ],
            "severity": "high",
            "description": "Test rule"
        }
        
        is_valid, error = engine.validate_rule_structure(valid_rule)
        assert is_valid is True
        assert error is None
    
    def test_rule_evaluation(self, test_data):
        """Test rule evaluation against data"""
        engine = RuleEngine()
        
        rule = {
            "rule_id": str(uuid4()),
            "conditions": [
                {
                    "field": "Amount Paid",
                    "operator": ">",
                    "value": 10000,
                    "logical_group": "A"
                }
            ],
            "logical_operator": "AND",
            "severity": "high",
            "description": "Large transactions"
        }
        
        violations = engine.evaluate_rule(rule, test_data)
        
        # Should find 2 violations (15000 and 25000)
        assert len(violations) == 2
        assert violations.iloc[0]["Amount Paid"] == 15000
        assert violations.iloc[1]["Amount Paid"] == 25000
    
    def test_explanation_generation(self, test_data):
        """Test explanation generation"""
        engine = RuleEngine()
        
        rule = {
            "rule_id": str(uuid4()),
            "conditions": [
                {
                    "field": "Amount Paid",
                    "operator": ">",
                    "value": 10000,
                    "logical_group": "A"
                }
            ],
            "severity": "high",
            "description": "Large transactions",
            "policy_reference": "AML Policy v2.1 Section 3.2"
        }
        
        record = test_data.iloc[0]
        explanation = engine.build_explanation(rule, record)
        
        assert "explanation_text" in explanation
        assert "field_evaluated" in explanation
        assert "actual_value" in explanation
        assert "expected_condition" in explanation
        assert "policy_reference" in explanation
        assert "Amount Paid" in explanation["field_evaluated"]
        assert "15000" in explanation["actual_value"]
    
    def test_risk_score_calculation(self):
        """Test risk score calculation"""
        engine = RuleEngine()
        
        # Test critical severity
        score = engine.calculate_risk_score("critical", 0.0, False, 1)
        assert score > 0
        assert score <= 100
        
        # Test with anomaly score
        score_with_anomaly = engine.calculate_risk_score("critical", 0.8, False, 1)
        assert score_with_anomaly > score
        
        # Test with recurrence
        score_recurring = engine.calculate_risk_score("critical", 0.0, True, 3)
        assert score_recurring > score


class TestScanHistory:
    """Test scan history tracking"""
    
    @pytest.mark.asyncio
    async def test_scan_creates_history(self, db_session, test_org, test_user, test_policy, test_rule, test_data):
        """Test that scan creates history record"""
        engine = ComplianceEngine(db_session)
        
        # Mock data fetching
        async def mock_fetch_data(org_id, connector_id, limit):
            return test_data
        
        engine._fetch_data = mock_fetch_data
        
        # Run scan
        result = await engine.scan_all_policies(
            org_id=test_org.org_id,
            user_id=test_user.user_id,
            limit=100
        )
        
        # Verify scan history created
        assert "scan_id" in result
        
        scan = db_session.query(ScanHistory).filter(
            ScanHistory.scan_id == result["scan_id"]
        ).first()
        
        assert scan is not None
        assert scan.org_id == test_org.org_id
        assert scan.initiated_by == test_user.user_id
        assert scan.status == "completed"
        assert scan.violations_detected > 0
        assert scan.risk_score is not None
    
    def test_scan_history_metrics(self, db_session, test_org, test_user):
        """Test scan history metrics calculation"""
        # Create multiple scan records
        for i in range(3):
            scan = ScanHistory(
                org_id=test_org.org_id,
                initiated_by=test_user.user_id,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                duration_seconds=10.0 + i,
                records_processed=1000,
                violations_detected=10 + i,
                risk_score=50.0 + i * 5,
                status="completed"
            )
            db_session.add(scan)
        
        db_session.commit()
        
        # Query scans
        scans = db_session.query(ScanHistory).filter(
            ScanHistory.org_id == test_org.org_id
        ).all()
        
        assert len(scans) == 3
        
        # Calculate average duration
        avg_duration = sum(s.duration_seconds for s in scans) / len(scans)
        assert avg_duration > 0


class TestViolationExplainability:
    """Test violation explainability"""
    
    def test_violation_has_explainability_fields(self, db_session, test_org, test_policy, test_rule):
        """Test violation includes all explainability fields"""
        violation = Violation(
            rule_id=test_rule.rule_id,
            policy_id=test_policy.policy_id,
            org_id=test_org.org_id,
            severity="high",
            explanation_text="Transaction amount 15,200 exceeded threshold 10,000",
            field_evaluated="Amount Paid",
            actual_value="15200",
            expected_condition="Amount Paid <= 10000",
            policy_reference="AML Policy v2.1 Section 3.2",
            status=ViolationStatus.PENDING
        )
        
        db_session.add(violation)
        db_session.commit()
        db_session.refresh(violation)
        
        assert violation.explanation_text is not None
        assert violation.field_evaluated == "Amount Paid"
        assert violation.actual_value == "15200"
        assert violation.expected_condition == "Amount Paid <= 10000"
        assert violation.policy_reference == "AML Policy v2.1 Section 3.2"


class TestRecurrenceTracking:
    """Test violation recurrence tracking"""
    
    def test_recurrence_detection(self, db_session, test_org, test_policy, test_rule):
        """Test recurring violation detection"""
        # Create first violation
        violation1 = Violation(
            rule_id=test_rule.rule_id,
            policy_id=test_policy.policy_id,
            org_id=test_org.org_id,
            record_id="TXN001",
            severity="high",
            explanation_text="First occurrence",
            field_evaluated="Amount Paid",
            actual_value="15000",
            expected_condition="Amount Paid <= 10000",
            policy_reference="AML Policy v2.1",
            occurrence_count=1,
            is_recurring=False,
            status=ViolationStatus.PENDING
        )
        
        db_session.add(violation1)
        db_session.commit()
        
        # Simulate second detection (update existing)
        violation1.occurrence_count += 1
        violation1.is_recurring = True
        violation1.last_detected_at = datetime.utcnow()
        db_session.commit()
        
        # Verify recurrence
        assert violation1.occurrence_count == 2
        assert violation1.is_recurring is True


class TestReviewWorkflow:
    """Test review workflow with logging"""
    
    def test_review_creates_log(self, db_session, test_org, test_user, test_policy, test_rule):
        """Test that review creates log entry"""
        # Create violation
        violation = Violation(
            rule_id=test_rule.rule_id,
            policy_id=test_policy.policy_id,
            org_id=test_org.org_id,
            severity="high",
            explanation_text="Test violation",
            field_evaluated="Amount Paid",
            actual_value="15000",
            expected_condition="Amount Paid <= 10000",
            policy_reference="AML Policy v2.1",
            final_risk_score=75.0,
            status=ViolationStatus.PENDING
        )
        
        db_session.add(violation)
        db_session.commit()
        db_session.refresh(violation)
        
        # Review violation
        previous_status = violation.status
        previous_risk = violation.final_risk_score
        
        violation.status = ViolationStatus.REVIEWED
        violation.reviewed_at = datetime.utcnow()
        violation.reviewed_by = test_user.user_id
        
        # Create review log
        log = ReviewLog(
            violation_id=violation.violation_id,
            org_id=test_org.org_id,
            reviewer_id=test_user.user_id,
            reviewer_role=test_user.role,
            action="confirm",
            previous_status=previous_status,
            new_status=ViolationStatus.REVIEWED,
            justification="Verified violation",
            reviewed_at=datetime.utcnow(),
            time_to_review_hours=2.5,
            risk_score_before=previous_risk,
            risk_score_after=violation.final_risk_score
        )
        
        db_session.add(log)
        db_session.commit()
        
        # Verify log created
        logs = db_session.query(ReviewLog).filter(
            ReviewLog.violation_id == violation.violation_id
        ).all()
        
        assert len(logs) == 1
        assert logs[0].action == "confirm"
        assert logs[0].justification == "Verified violation"
        assert logs[0].time_to_review_hours == 2.5


class TestEndToEndFlow:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_compliance_flow(self, db_session, test_org, test_user, test_policy, test_rule, test_data):
        """Test complete flow: scan → detect → review → audit"""
        engine = ComplianceEngine(db_session)
        
        # Mock data fetching
        async def mock_fetch_data(org_id, connector_id, limit):
            return test_data
        
        engine._fetch_data = mock_fetch_data
        
        # Step 1: Run scan
        result = await engine.scan_all_policies(
            org_id=test_org.org_id,
            user_id=test_user.user_id,
            limit=100
        )
        
        assert result["total_violations"] > 0
        scan_id = result["scan_id"]
        
        # Step 2: Verify scan history
        scan = db_session.query(ScanHistory).filter(
            ScanHistory.scan_id == scan_id
        ).first()
        
        assert scan is not None
        assert scan.status == "completed"
        
        # Step 3: Get violations
        violations = db_session.query(Violation).filter(
            Violation.scan_id == scan_id
        ).all()
        
        assert len(violations) > 0
        
        # Step 4: Review first violation
        violation = violations[0]
        previous_status = violation.status
        
        violation.status = ViolationStatus.REVIEWED
        violation.reviewed_at = datetime.utcnow()
        violation.reviewed_by = test_user.user_id
        
        # Create review log
        log = ReviewLog(
            violation_id=violation.violation_id,
            org_id=test_org.org_id,
            reviewer_id=test_user.user_id,
            reviewer_role=test_user.role,
            action="confirm",
            previous_status=previous_status,
            new_status=ViolationStatus.REVIEWED,
            justification="End-to-end test review",
            reviewed_at=datetime.utcnow()
        )
        
        db_session.add(log)
        db_session.commit()
        
        # Step 5: Verify complete audit trail
        review_logs = db_session.query(ReviewLog).filter(
            ReviewLog.violation_id == violation.violation_id
        ).all()
        
        assert len(review_logs) == 1
        assert review_logs[0].justification == "End-to-end test review"
        
        # Verify data consistency
        assert violation.status == ViolationStatus.REVIEWED
        assert violation.reviewed_by == test_user.user_id
        assert scan.violations_detected == len(violations)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
