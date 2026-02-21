# ⚡ NitiLens Governance - Quick Reference

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Initialize database (includes new tables)
python backend/init_db.py

# Start application
uvicorn app.main:app --reload --port 8000
```

## 📊 New API Endpoints

### Remediation
```bash
GET    /api/remediation                    # List cases
GET    /api/remediation/{id}               # Case details
POST   /api/remediation/update-status/{id} # Update status
POST   /api/remediation/comment/{id}       # Add comment
POST   /api/remediation/assign/{id}        # Reassign
GET    /api/remediation/stats/summary      # Statistics
```

### Policy Impact
```bash
POST   /api/policy-impact/analyze          # Analyze change
GET    /api/policy-impact/history/{id}     # Change history
GET    /api/policy-impact/report/{id}      # Impact report
```

### Risk & Anomaly
```bash
POST   /api/risk/train-model               # Train ML model
GET    /api/risk/anomalies                 # Get anomalies
GET    /api/risk/heatmap                   # Risk heatmap
GET    /api/risk/trend                     # Current trend
GET    /api/risk/trends/history            # Historical trends
GET    /api/risk/dashboard                 # Full dashboard
```

## 🔄 Workflow Examples

### 1. Violation → Remediation

```python
# Violation detected automatically creates case
violation = create_violation(severity="high", ...)

# Case auto-created with:
# - Recommended action
# - Priority (HIGH)
# - Due date (72 hours)
# - Auto-assigned user
# - Alert sent
```

### 2. Policy Update → Impact Analysis

```python
# Analyze impact
impact = analyzer.analyze_policy_update(old_policy_id, new_policy_id)

# Returns:
# - Changes detected (new/modified/removed)
# - Old vs new violation counts
# - Net risk delta
# - Risk change percentage
```

### 3. Anomaly Detection

```python
# Train model (one-time per org)
detector.train_model(org_id, transaction_data)

# Detect anomalies
data_with_scores = detector.detect_anomalies(org_id, new_data)

# Flagged if anomaly_score > 0.75
```

## 📋 Database Schema

### New Tables

```sql
-- Remediation
remediation_cases (case_id, violation_id, assigned_to, status, priority, due_date, ...)
remediation_comments (comment_id, case_id, user_id, comment_text, ...)

-- Policy Impact
policy_change_log (change_id, policy_id, old_rule_id, new_rule_id, change_type, ...)

-- Anomaly Detection
transactions (transaction_id, amount, anomaly_score, is_anomalous, ...)
risk_trends (trend_id, org_id, week_start, avg_risk_score, trend_direction, ...)
```

### Updated Tables

```sql
-- Rules (versioning)
ALTER TABLE rules ADD COLUMN previous_rule_id UUID;
ALTER TABLE rules ADD COLUMN is_active BOOLEAN;
ALTER TABLE rules ADD COLUMN effective_from TIMESTAMP;

-- Violations (risk scoring)
ALTER TABLE violations ADD COLUMN rule_severity_score FLOAT;
ALTER TABLE violations ADD COLUMN anomaly_score FLOAT;
ALTER TABLE violations ADD COLUMN final_risk_score FLOAT;
```

## 🎯 Key Features

### Auto-Recommendation
- **Threshold** → File regulatory report
- **Frequency** → Enhanced due diligence
- **Pattern** → AML investigation
- **Comparison** → Verification required

### Auto-Assignment
- **Critical** → Compliance Admin
- **High** → Senior Reviewer
- **Medium** → Reviewer
- **Low** → Junior Analyst

### Escalation
- Overdue → Status changed
- 48+ hours → Auto-escalate to admin

### Risk Scoring
```
final_risk = (rule_severity * 0.7) + (anomaly_score * 100 * 0.3)
```

## 🔧 Configuration

### ML Model
```python
# Isolation Forest parameters
contamination = 0.1  # Expect 10% anomalies
n_estimators = 100   # 100 trees
threshold = 0.75     # Anomaly flag threshold
```

### Remediation
```python
# Due dates by priority
CRITICAL = 24 hours
HIGH = 72 hours
MEDIUM = 168 hours (7 days)
LOW = 336 hours (14 days)

# Escalation
ESCALATION_THRESHOLD = 48 hours
```

### Risk Alerts
```python
# Trend alert threshold
RISK_INCREASE_ALERT = 20%  # Alert if risk increases >20%
```

## 📊 Statistics

### Remediation Stats
```json
{
  "total_cases": 150,
  "open": 25,
  "in_progress": 40,
  "escalated": 5,
  "overdue": 10,
  "completed": 70,
  "critical_pending": 3,
  "completion_rate": 46.67
}
```

### Risk Trend
```json
{
  "current_week_avg_risk": 65.5,
  "previous_week_avg_risk": 52.3,
  "risk_change_percent": 25.24,
  "trend": "increasing",
  "alert_message": "⚠️ Compliance Risk Increasing"
}
```

## 🧪 Testing

### Test Remediation
```bash
# Create violation
curl -X POST /api/compliance/scan \
  -H "Authorization: Bearer $TOKEN"

# Check case created
curl /api/remediation \
  -H "Authorization: Bearer $TOKEN"
```

### Test Policy Impact
```bash
# Analyze impact
curl -X POST /api/policy-impact/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"old_policy_id": "uuid1", "new_policy_id": "uuid2"}'
```

### Test Anomaly Detection
```bash
# Train model
curl -X POST /api/risk/train-model \
  -H "Authorization: Bearer $TOKEN"

# Get anomalies
curl /api/risk/anomalies?threshold=0.75 \
  -H "Authorization: Bearer $TOKEN"
```

## 🎨 Frontend Components

### Remediation Dashboard
```typescript
<RemediationDashboard>
  <KanbanBoard>
    <Column status="open" />
    <Column status="in_progress" />
    <Column status="escalated" />
    <Column status="completed" />
  </KanbanBoard>
  <CaseDetails />
  <CommentThread />
</RemediationDashboard>
```

### Policy Impact Report
```typescript
<PolicyImpactReport>
  <ChangesSummary />
  <ThresholdComparison />
  <ViolationDelta />
  <RiskTrendChart />
</PolicyImpactReport>
```

### Anomaly Detection
```typescript
<AnomalyDashboard>
  <AnomalyList threshold={0.75} />
  <RiskHeatmap />
  <TrendChart weeks={12} />
  <AlertBanner />
</AnomalyDashboard>
```

## 🔍 Troubleshooting

### ML Model Not Training
```python
# Check data availability
transactions = db.query(Transaction).count()
# Need at least 100 transactions

# Check model directory
os.makedirs("models/anomaly", exist_ok=True)
```

### Cases Not Auto-Creating
```python
# Check remediation engine integration
from app.services.remediation_engine import RemediationEngine
engine = RemediationEngine(db)
case = await engine.create_remediation_case(violation)
```

### Escalations Not Running
```python
# Check scheduler
from app.core.scheduler_enhanced import start_enhanced_scheduler
start_enhanced_scheduler()
```

## 📚 Documentation

- **Full Features**: GOVERNANCE-FEATURES.md
- **Implementation**: GOVERNANCE-IMPLEMENTATION.md
- **API Docs**: http://localhost:8000/docs

## 🎯 Success Checklist

- ✅ Violations auto-create remediation cases
- ✅ Cases auto-assigned to users
- ✅ Overdue cases escalate automatically
- ✅ Policy changes generate impact reports
- ✅ ML model detects anomalies
- ✅ Risk trends calculated weekly
- ✅ Combined risk scoring active
- ✅ All endpoints working

---

**Quick Reference Version**: 3.0.0  
**Last Updated**: 2024-02-21
