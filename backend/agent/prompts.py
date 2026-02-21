"""
NitiGuard AI Prompt Templates
Strict system prompts to prevent hallucination
"""

SYSTEM_PROMPT = """You are NitiGuard AI, the compliance assistant for NitiLens RegTech platform.

CRITICAL RULES:
1. Answer ONLY using the provided system data
2. NEVER hallucinate or guess numbers
3. If data is not available, say "Data not available in current context"
4. Be precise, professional, and compliance-focused
5. Always cite sources when referencing specific violations or policies
6. Use exact numbers from the context - do not round or estimate
7. Maintain professional regulatory language

YOUR ROLE:
- Explain compliance risks and violations
- Provide audit summaries
- Answer policy questions
- Explain remediation status
- Analyze trends

RESPONSE FORMAT:
- Start with direct answer
- Provide supporting data
- Include relevant references
- Keep responses concise but complete
- Use bullet points for multiple items

SECURITY:
- Respect user role permissions
- Never expose data from other organizations
- Flag sensitive information appropriately
"""

INTENT_CLASSIFIER_PROMPT = """Classify the user's intent into ONE of these categories:

1. risk_inquiry - Questions about risk scores, risk levels, compliance status
2. violation_explanation - Questions about specific violations or why something was flagged
3. policy_clarification - Questions about policies, rules, or regulatory requirements
4. remediation_status - Questions about remediation cases, open issues, or resolution progress
5. trend_summary - Questions about trends, changes over time, or comparisons
6. audit_summary - Requests for summaries, reports, or overviews
7. action_request - Requests to perform actions (mark, update, create)
8. general_help - General questions about the system or how to use features

User message: "{message}"

Respond with ONLY the category name, nothing else."""

CONTEXT_TEMPLATES = {
    "risk_inquiry": """
CURRENT SYSTEM STATUS:
- Risk Score: {risk_score}/100 ({risk_level})
- Risk Trend: {risk_trend}
- Total Violations: {total_violations}
- Critical Violations: {critical_violations}
- High Violations: {high_violations}
- Medium Violations: {medium_violations}
- Low Violations: {low_violations}
- Recurring Violations: {recurring_violations}
- Open Remediation Cases: {open_cases}
- Overdue Cases: {overdue_cases}
- Last Scan: {last_scan_time}
- Active Policies: {active_policies}
- Active Rules: {active_rules}
""",
    
    "violation_explanation": """
VIOLATION DETAILS:
- Violation ID: {violation_id}
- Severity: {severity}
- Status: {status}
- Detected: {detected_at}
- Explanation: {explanation_text}
- Field Evaluated: {field_evaluated}
- Actual Value: {actual_value}
- Expected Condition: {expected_condition}
- Policy Reference: {policy_reference}
- Risk Score: {risk_score}
- Is Recurring: {is_recurring}
- Occurrence Count: {occurrence_count}
- Evidence: {evidence}
""",
    
    "policy_clarification": """
POLICY INFORMATION:
- Policy Name: {policy_name}
- Version: {version}
- Department: {department}
- Regulatory Framework: {framework}
- Status: {status}
- Active Rules: {rule_count}
- Uploaded: {uploaded_at}
- Description: {description}
""",
    
    "remediation_status": """
REMEDIATION OVERVIEW:
- Total Cases: {total_cases}
- Open Cases: {open_cases}
- In Progress: {in_progress}
- Escalated: {escalated}
- Overdue: {overdue}
- Completed: {completed}
- Critical Pending: {critical_pending}
- Completion Rate: {completion_rate}%

RECENT CASES:
{recent_cases}
""",
    
    "trend_summary": """
TREND ANALYSIS:
- Current Risk Score: {current_risk}
- Previous Risk Score: {previous_risk}
- Change: {risk_change}
- Trend Direction: {trend_direction}
- Violations This Period: {current_violations}
- Violations Last Period: {previous_violations}
- New Violations: {new_violations}
- Recurring Violations: {recurring_violations}
- Time Period: {time_period}
""",
    
    "audit_summary": """
AUDIT SUMMARY:
- Scan ID: {scan_id}
- Scan Date: {scan_date}
- Duration: {duration} seconds
- Records Processed: {records_processed}
- Policies Scanned: {policies_scanned}
- Rules Executed: {rules_executed}
- Violations Detected: {violations_detected}
  - Critical: {critical_violations}
  - High: {high_violations}
  - Medium: {medium_violations}
  - Low: {low_violations}
- Risk Score: {risk_score}/100
- Status: {status}
"""
}

def get_risk_level(risk_score: float) -> str:
    """Convert risk score to risk level"""
    if risk_score >= 75:
        return "High Risk"
    elif risk_score >= 50:
        return "Moderate Risk"
    elif risk_score >= 25:
        return "Low Risk"
    else:
        return "Minimal Risk"

def build_user_prompt(intent: str, context_data: dict, user_message: str) -> str:
    """Build complete user prompt with context"""
    template = CONTEXT_TEMPLATES.get(intent, "")
    
    try:
        context = template.format(**context_data)
    except KeyError as e:
        context = f"Context data incomplete: {e}"
    
    prompt = f"""SYSTEM CONTEXT:
{context}

USER QUESTION:
{user_message}

Provide a clear, accurate answer based ONLY on the context provided above. Do not make assumptions or add information not present in the context."""
    
    return prompt

def build_action_confirmation_prompt(action: str, details: dict) -> str:
    """Build prompt for action confirmation"""
    return f"""The user wants to perform the following action:

ACTION: {action}
DETAILS: {details}

Before proceeding, confirm:
1. Is this action safe and appropriate?
2. Does the user have permission for this action?
3. What are the consequences?

Respond with a confirmation message explaining what will happen."""
