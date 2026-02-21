"""
PDF text extraction using PyMuPDF (fitz).
Falls back to a stub string if the library is unavailable or file is not a valid PDF.
"""
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """Extract raw text from a PDF file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        doc.close()
        full_text = "\n".join(pages_text)
        if full_text.strip():
            return full_text
        return _stub_policy_text(file_path)
    except Exception:
        return _stub_policy_text(file_path)


def _stub_policy_text(file_path: str) -> str:
    """Return a rich AML/GDPR policy stub for demo when PDF parsing is unavailable."""
    name = Path(file_path).stem.lower()
    if "aml" in name or "anti" in name:
        return AML_POLICY_STUB
    return GDPR_POLICY_STUB


AML_POLICY_STUB = """
ANTI-MONEY LAUNDERING (AML) COMPLIANCE POLICY — Version 2.1

Section 1: Purpose
This policy establishes requirements for detecting, preventing, and reporting money laundering activities
in accordance with the Bank Secrecy Act (BSA), FinCEN guidance, and FATF recommendations.

Section 2: Definitions
- Money Laundering: Concealing the origin of illegally obtained money.
- CTR: Currency Transaction Report — required for cash transactions exceeding $10,000.
- SAR: Suspicious Activity Report — required when suspicious patterns are identified.

Section 3: Transaction Monitoring Rules
3.1 Currency Transaction Reporting
All single transactions exceeding $10,000 in value must be flagged for CTR filing within 15 business days.

3.2 Aggregate Thresholds
Multiple transactions by the same individual totaling $10,000 or more within a single business day
must be treated as a single large transaction.

3.3 Rapid Transfer Detection
Any account executing more than 5 transfers to the same beneficiary within a 24-hour window
must be flagged as a potential layering pattern.

3.4 Enhanced Due Diligence
Cheque or wire transfers exceeding $50,000 require enhanced customer due diligence (EDD) documentation.

Section 4: Suspicious Patterns
4.1 Structuring (Smurfing)
Transactions structured as round numbers (multiples of $1,000) above $5,000 with no apparent
business rationale may indicate deliberate structuring to avoid reporting thresholds.

4.2 Layering via Currency Conversion
When the payment currency differs from the receiving currency, enhanced scrutiny is required
to detect laundering through foreign exchange channels.

4.3 Velocity Anomalies
Any account with transaction frequency more than 3 standard deviations from its historical
monthly average must be reviewed by the compliance team.

Section 5: Reporting Requirements
5.1 All violations must be escalated to the AML Compliance Officer within 24 hours.
5.2 Confirmed laundering activity must be reported to FinCEN via SAR within 30 calendar days.
5.3 All flagged transactions must be documented with: transaction ID, amount, parties, and justification.

Section 6: Penalties for Non-Compliance
Failure to report qualifying transactions may result in civil penalties up to $1,000,000 per violation
and criminal prosecution under 31 U.S.C. § 5322.
"""

GDPR_POLICY_STUB = """
GENERAL DATA PROTECTION REGULATION (GDPR) COMPLIANCE POLICY — Version 1.4

Article 5: Principles of Data Processing
Personal data must be processed lawfully, fairly, and transparently.
Data must be collected for specified, explicit, and legitimate purposes.
Data must be adequate, relevant, and limited to what is necessary (data minimization).
Data must be accurate and kept up to date.
Data must not be kept longer than necessary (storage limitation).
Data must be processed securely (integrity and confidentiality).

Article 17: Right to Erasure
Upon valid request, personal data must be deleted within 30 days.
Any system retaining data beyond this window after an erasure request is in violation.

Article 25: Data Protection by Design
Systems must implement data protection measures from the design stage.
Default settings must be set to the most privacy-preserving option.

Article 32: Security of Processing
Organizations must implement appropriate technical measures including encryption,
pseudonymization, and access controls to protect personal data.

Article 33: Breach Notification
Any personal data breach must be reported to the supervisory authority within 72 hours of discovery.
Affected individuals must be notified without undue delay if the breach poses a high risk.
"""
