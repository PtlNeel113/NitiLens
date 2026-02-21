from pydantic import BaseModel
from typing import Literal, Optional


class ReviewAction(BaseModel):
    action: Literal["resolve", "dismiss", "false_positive", "escalate"]
    comment: Optional[str] = None
    reviewed_by: str = "compliance_officer"
