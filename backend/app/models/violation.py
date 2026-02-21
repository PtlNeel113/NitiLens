from pydantic import BaseModel
from typing import Any, Dict, Literal, Optional


class Violation(BaseModel):
    id: str
    transaction_id: str
    rule_id: str
    rule_name: str
    severity: Literal["critical", "high", "medium", "low"]
    explanation: str
    evidence: Dict[str, Any]
    status: Literal["open", "reviewed", "resolved", "false_positive"] = "open"
    reviewer_comment: Optional[str] = None
    detected_at: str
    reviewed_at: Optional[str] = None
