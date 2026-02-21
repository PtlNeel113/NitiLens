from pydantic import BaseModel
from typing import Literal, Optional


class PolicyRule(BaseModel):
    id: str
    description: str
    condition: str
    severity: Literal["critical", "high", "medium", "low"]
    source_reference: str
    category: str
    approved: bool = False
    policy_id: Optional[str] = None
