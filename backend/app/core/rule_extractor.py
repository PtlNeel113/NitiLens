"""
Rule extractor: parses raw policy text and maps keywords to structured compliance rules.
Works without an LLM — uses pattern matching on known AML/GDPR terminology.
"""
import re
import uuid
from typing import List
from app.models.rule import PolicyRule


# Keyword → rule template mapping
_AML_RULE_TEMPLATES = [
    {
        "keywords": ["10,000", "$10,000", "10000", "ctr", "currency transaction report"],
        "id_prefix": "ext-aml-ctr",
        "description": "Single transaction exceeding $10,000 must be reported (CTR)",
        "condition": "Amount Paid > 10000",
        "severity": "critical",
        "category": "Large Transaction Reporting",
    },
    {
        "keywords": ["structuring", "smurfing", "round", "1,000"],
        "id_prefix": "ext-aml-struct",
        "description": "Round-number transactions above $5,000 may indicate structuring",
        "condition": "Amount Paid % 1000 == 0 AND Amount Paid > 5000",
        "severity": "medium",
        "category": "Structuring",
    },
    {
        "keywords": ["rapid transfer", "5 transfer", "24 hour", "24-hour", "layering"],
        "id_prefix": "ext-aml-rapid",
        "description": "More than 5 transfers to the same beneficiary within 24 hours",
        "condition": "count(To Account, 24h) > 5",
        "severity": "high",
        "category": "Suspicious Activity",
    },
    {
        "keywords": ["currency conversion", "cross-currency", "foreign exchange", "mixing"],
        "id_prefix": "ext-aml-fx",
        "description": "Payment currency differs from receiving currency (layering risk)",
        "condition": "Payment Currency != Receiving Currency",
        "severity": "medium",
        "category": "Currency Risk",
    },
    {
        "keywords": ["50,000", "$50,000", "50000", "enhanced due diligence", "edd", "wire"],
        "id_prefix": "ext-aml-edd",
        "description": "Wire/cheque over $50,000 requires enhanced due diligence",
        "condition": "Amount Paid > 50000 AND Payment Format IN ['Cheque', 'Wire']",
        "severity": "high",
        "category": "Enhanced Due Diligence",
    },
]

_GDPR_RULE_TEMPLATES = [
    {
        "keywords": ["erasure", "right to be forgotten", "delete", "30 days"],
        "id_prefix": "ext-gdpr-erasure",
        "description": "Personal data must be deleted within 30 days of erasure request",
        "condition": "days_since_erasure_request <= 30",
        "severity": "critical",
        "category": "Data Erasure",
    },
    {
        "keywords": ["breach notification", "72 hours", "supervisory authority"],
        "id_prefix": "ext-gdpr-breach",
        "description": "Data breach must be reported within 72 hours of discovery",
        "condition": "hours_since_breach_discovery <= 72",
        "severity": "critical",
        "category": "Breach Notification",
    },
    {
        "keywords": ["data minimization", "adequate", "relevant", "limited"],
        "id_prefix": "ext-gdpr-min",
        "description": "Only collect data adequate and relevant to stated purpose",
        "condition": "data_minimization_compliant == true",
        "severity": "medium",
        "category": "Data Minimization",
    },
]


def extract_rules_from_text(policy_text: str, policy_id: str, source_name: str) -> List[PolicyRule]:
    """
    Extract compliance rules from raw policy text using keyword matching.
    Returns a list of PolicyRule objects awaiting human approval.
    """
    text_lower = policy_text.lower()
    extracted: List[PolicyRule] = []

    all_templates = _AML_RULE_TEMPLATES + _GDPR_RULE_TEMPLATES

    for template in all_templates:
        # Check if any keyword appears in the policy text
        if any(kw in text_lower for kw in template["keywords"]):
            # Find the most relevant sentence for source reference
            source_ref = _find_source_sentence(policy_text, template["keywords"])
            rule = PolicyRule(
                id=f"{template['id_prefix']}-{uuid.uuid4().hex[:6]}",
                description=template["description"],
                condition=template["condition"],
                severity=template["severity"],
                source_reference=source_ref or f"{source_name} — auto-extracted",
                category=template["category"],
                approved=False,
                policy_id=policy_id,
            )
            extracted.append(rule)

    return extracted


def _find_source_sentence(text: str, keywords: List[str]) -> str:
    """Find the sentence in the text most relevant to the given keywords."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for kw in keywords:
        for sentence in sentences:
            if kw.lower() in sentence.lower():
                # Return a truncated version
                clean = sentence.strip().replace('\n', ' ')
                return clean[:150] + ('...' if len(clean) > 150 else '')
    return ""
