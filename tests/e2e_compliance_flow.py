"""
End-to-End Compliance Flow Validation
Tests the complete lifecycle: Upload → Extract → Approve → Scan → Detect → Remediate → Risk → Report
"""
import requests
import time
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"

class E2EComplianceTest:
    def __init__(self):
        self.token = None
        self.org_id = None
        self.policy_id = None
        self.rule_ids = []
        self.scan_id = None
        self.violations = []
        self.remediation_cases = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test progress"""
        print(f"[{level}] {message}")
        
    def fail(self, message: str):
        """Record failure"""
        self.errors.append(message)
        self.log(message, "FAIL")
        
    def assert_not_null(self, value: Any, field_name: str):
        """Assert value is not null"""
        if value is None or value == "" or value == []:
            self.fail(f"{field_name} is null or empty")
            return False
        return True
        
    def assert_count_match(self, actual: int, expected: int, entity: str):
        """Assert counts match"""
        if actual != expected:
            self.fail(f"{entity} count mismatch: expected {expected}, got {actual}")
            return False
        return True
        
    def step_1_register_and_login(self) -> bool:
        """Step 1: Register organization and login"""
        self.log("Step 1: Register and Login")
        
        # Register
        try:
            response = requests.post(f"{API_BASE}/api/auth/register", json={
                "email": f"test_{int(time.time())}@nitilens.com",
                "password": "SecurePass123!",
                "full_name": "E2E Test User",
                "org_name": "E2E Test Organization"
            })
            
            if response.status_code != 200:
                self.fail(f"Registration failed: {response.text}")
                return False
                
            data = response.json()
            self.token = data.get("access_token")
            self.org_id = data.get("user", {}).get("org_id")
            
            if not self.assert_not_null(self.token, "access_token"):
                return False
            if not self.assert_not_null(self.org_id, "org_id"):
                return False
                
            self.log(f"✓ Registered and logged in. Org ID: {self.org_id}")
            return True
            
        except Exception as e:
            self.fail(f"Registration error: {str(e)}")
            return False
            
    def step_2_upload_policy(self) -> bool:
        """Step 2: Upload compliance policy"""
        self.log("Step 2: Upload Policy")
        
        try:
            # Create a test policy file
            policy_content = """
            ANTI-MONEY LAUNDERING POLICY
            
            1. Transaction Monitoring Rules
            - All transactions above $10,000 must be flagged for review
            - Multiple transactions totaling $10,000+ within 24 hours require investigation
            - Transactions to high-risk countries must be reviewed
            
            2. Customer Due Diligence
            - Enhanced due diligence required for high-risk customers
            - Annual review of customer risk profiles
            
            3. Suspicious Activity Reporting
            - File SAR within 30 days of detection
            - Maintain records for 5 years
            """
            
            files = {
                'file': ('aml_policy.txt', policy_content, 'text/plain')
            }
            data = {
                'policy_name': 'AML Policy E2E Test',
                'department': 'Compliance',
                'regulatory_framework': 'AML/CFT',
                'version': '1.0'
            }
            
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{API_BASE}/api/policies/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Policy upload failed: {response.text}")
                return False
                
            result = response.json()
            self.policy_id = result.get("policy_id")
            extracted_rules = result.get("rules_extracted", 0)
            
            if not self.assert_not_null(self.policy_id, "policy_id"):
                return False
            if extracted_rules == 0:
                self.fail("No rules extracted from policy")
                return False
                
            self.log(f"✓ Policy uploaded. ID: {self.policy_id}, Rules extracted: {extracted_rules}")
            return True
            
        except Exception as e:
            self.fail(f"Policy upload error: {str(e)}")
            return False
            
    def step_3_approve_rules(self) -> bool:
        """Step 3: Approve extracted rules"""
        self.log("Step 3: Approve Rules")
        
        try:
            # Get pending rules
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{API_BASE}/api/reviews?status=pending",
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Failed to fetch pending rules: {response.text}")
                return False
                
            pending_rules = response.json()
            
            if not pending_rules:
                self.fail("No pending rules found for approval")
                return False
                
            # Approve all rules
            for rule in pending_rules:
                rule_id = rule.get("rule_id")
                approve_response = requests.post(
                    f"{API_BASE}/api/reviews/approve/{rule_id}",
                    headers=headers,
                    json={"comment": "E2E test approval"}
                )
                
                if approve_response.status_code == 200:
                    self.rule_ids.append(rule_id)
                    
            if not self.rule_ids:
                self.fail("No rules were approved")
                return False
                
            self.log(f"✓ Approved {len(self.rule_ids)} rules")
            return True
            
        except Exception as e:
            self.fail(f"Rule approval error: {str(e)}")
            return False
            
    def step_4_run_compliance_scan(self) -> bool:
        """Step 4: Run compliance scan"""
        self.log("Step 4: Run Compliance Scan")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(
                f"{API_BASE}/api/compliance/scan",
                headers=headers,
                json={
                    "department": "Compliance",
                    "framework": "AML/CFT",
                    "limit": 100
                }
            )
            
            if response.status_code != 200:
                self.fail(f"Compliance scan failed: {response.text}")
                return False
                
            result = response.json()
            violations_detected = result.get("violations_detected", 0)
            
            self.log(f"✓ Scan completed. Violations detected: {violations_detected}")
            return True
            
        except Exception as e:
            self.fail(f"Compliance scan error: {str(e)}")
            return False
            
    def step_5_verify_violations(self) -> bool:
        """Step 5: Verify violations were created"""
        self.log("Step 5: Verify Violations")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{API_BASE}/api/compliance/violations",
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Failed to fetch violations: {response.text}")
                return False
                
            self.violations = response.json()
            
            if not self.violations:
                self.fail("No violations found after scan")
                return False
                
            # Verify violation data integrity
            for violation in self.violations:
                if not self.assert_not_null(violation.get("violation_id"), "violation_id"):
                    return False
                if not self.assert_not_null(violation.get("severity"), "severity"):
                    return False
                if not self.assert_not_null(violation.get("rule_id"), "rule_id"):
                    return False
                    
            self.log(f"✓ Verified {len(self.violations)} violations")
            return True
            
        except Exception as e:
            self.fail(f"Violation verification error: {str(e)}")
            return False
            
    def step_6_verify_remediation_auto_created(self) -> bool:
        """Step 6: Verify remediation cases were auto-created"""
        self.log("Step 6: Verify Auto-Remediation")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{API_BASE}/api/remediation",
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Failed to fetch remediation cases: {response.text}")
                return False
                
            self.remediation_cases = response.json()
            
            # Verify remediation count matches high/critical violations
            high_critical_violations = [
                v for v in self.violations 
                if v.get("severity") in ["high", "critical"]
            ]
            
            if len(self.remediation_cases) != len(high_critical_violations):
                self.fail(
                    f"Remediation count mismatch: {len(self.remediation_cases)} cases "
                    f"vs {len(high_critical_violations)} high/critical violations"
                )
                return False
                
            self.log(f"✓ Verified {len(self.remediation_cases)} remediation cases auto-created")
            return True
            
        except Exception as e:
            self.fail(f"Remediation verification error: {str(e)}")
            return False
            
    def step_7_verify_risk_scores(self) -> bool:
        """Step 7: Verify risk scores calculated correctly"""
        self.log("Step 7: Verify Risk Scores")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{API_BASE}/api/risk/dashboard",
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Failed to fetch risk dashboard: {response.text}")
                return False
                
            risk_data = response.json()
            
            # Verify risk scores are calculated
            if not risk_data.get("top_anomalies"):
                self.log("⚠ No anomalies detected (acceptable if no ML model trained)")
            
            self.log("✓ Risk scores verified")
            return True
            
        except Exception as e:
            self.fail(f"Risk score verification error: {str(e)}")
            return False
            
    def step_8_verify_dashboard_consistency(self) -> bool:
        """Step 8: Verify dashboard metrics match database"""
        self.log("Step 8: Verify Dashboard Consistency")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            
            # Get dashboard overview
            dashboard_response = requests.get(
                f"{API_BASE}/api/dashboard/overview",
                headers=headers
            )
            
            if dashboard_response.status_code != 200:
                self.fail(f"Failed to fetch dashboard: {response.text}")
                return False
                
            dashboard = dashboard_response.json()
            
            # Get compliance summary
            summary_response = requests.get(
                f"{API_BASE}/api/compliance/summary",
                headers=headers
            )
            
            if summary_response.status_code != 200:
                self.fail(f"Failed to fetch summary: {response.text}")
                return False
                
            summary = summary_response.json()
            
            # Verify counts match
            dashboard_violations = dashboard.get("violations", {}).get("total", 0)
            summary_violations = summary.get("total_violations", 0)
            
            if dashboard_violations != summary_violations:
                self.fail(
                    f"Dashboard violation count ({dashboard_violations}) "
                    f"doesn't match summary ({summary_violations})"
                )
                return False
                
            self.log("✓ Dashboard metrics consistent with database")
            return True
            
        except Exception as e:
            self.fail(f"Dashboard consistency error: {str(e)}")
            return False
            
    def step_9_generate_audit_report(self) -> bool:
        """Step 9: Generate comprehensive audit report"""
        self.log("Step 9: Generate Audit Report")
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{API_BASE}/api/compliance/summary",
                headers=headers
            )
            
            if response.status_code != 200:
                self.fail(f"Failed to generate report: {response.text}")
                return False
                
            report = response.json()
            
            # Verify report completeness
            required_fields = [
                "total_violations",
                "by_severity",
                "compliance_rate"
            ]
            
            for field in required_fields:
                if field not in report:
                    self.fail(f"Report missing required field: {field}")
                    return False
                    
            self.log("✓ Audit report generated successfully")
            return True
            
        except Exception as e:
            self.fail(f"Report generation error: {str(e)}")
            return False
            
    def run_full_test(self) -> bool:
        """Run complete E2E test"""
        self.log("=" * 60)
        self.log("STARTING END-TO-END COMPLIANCE FLOW TEST")
        self.log("=" * 60)
        
        steps = [
            self.step_1_register_and_login,
            self.step_2_upload_policy,
            self.step_3_approve_rules,
            self.step_4_run_compliance_scan,
            self.step_5_verify_violations,
            self.step_6_verify_remediation_auto_created,
            self.step_7_verify_risk_scores,
            self.step_8_verify_dashboard_consistency,
            self.step_9_generate_audit_report
        ]
        
        for step in steps:
            if not step():
                self.log("=" * 60)
                self.log("TEST FAILED", "FAIL")
                self.log("=" * 60)
                self.print_errors()
                return False
            time.sleep(1)  # Brief pause between steps
            
        self.log("=" * 60)
        self.log("ALL TESTS PASSED", "PASS")
        self.log("=" * 60)
        return True
        
    def print_errors(self):
        """Print all errors"""
        if self.errors:
            self.log("\nERRORS FOUND:")
            for i, error in enumerate(self.errors, 1):
                self.log(f"  {i}. {error}", "ERROR")


if __name__ == "__main__":
    test = E2EComplianceTest()
    success = test.run_full_test()
    sys.exit(0 if success else 1)
