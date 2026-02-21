"""
API routes for human review of compliance violations.
"""
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Query
from app.core.violation_engine import load_violations, update_violation_status
from app.models.review import ReviewAction

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

_STATUS_MAP = {
    "resolve": "resolved",
    "dismiss": "false_positive",
    "false_positive": "false_positive",
    "escalate": "reviewed",
}


@router.get("", summary="List violations pending human review")
def list_review_queue(
    severity: Optional[Literal["critical", "high", "medium", "low"]] = None,
    limit: int = Query(default=50, ge=1, le=200),
):
    violations = load_violations()
    # Review queue shows only open + reviewed (not yet resolved or false_positive)
    queue = [v for v in violations if v.status in ("open", "reviewed")]
    if severity:
        queue = [v for v in queue if v.severity == severity]
    queue.sort(key=lambda v: {"critical": 0, "high": 1, "medium": 2, "low": 3}[v.severity])
    return {
        "total_pending": len(queue),
        "violations": [v.model_dump() for v in queue[:limit]],
    }


@router.post("/{violation_id}/action", summary="Take a review action on a violation")
def review_violation(violation_id: str, action: ReviewAction):
    new_status = _STATUS_MAP.get(action.action)
    if not new_status:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action.action}")

    updated = update_violation_status(violation_id, new_status, action.comment)
    if not updated:
        raise HTTPException(status_code=404, detail="Violation not found")

    return {
        "violation_id": violation_id,
        "new_status": new_status,
        "reviewed_by": action.reviewed_by,
        "comment": action.comment,
        "message": f"Violation {violation_id} marked as '{new_status}'.",
    }


@router.get("/stats", summary="Review queue statistics")
def review_stats():
    violations = load_violations()
    open_v = [v for v in violations if v.status == "open"]
    reviewed_v = [v for v in violations if v.status == "reviewed"]
    resolved_v = [v for v in violations if v.status == "resolved"]
    false_pos = [v for v in violations if v.status == "false_positive"]

    critical_open = [v for v in open_v if v.severity == "critical"]

    return {
        "open": len(open_v),
        "reviewed": len(reviewed_v),
        "resolved": len(resolved_v),
        "false_positives": len(false_pos),
        "critical_open": len(critical_open),
        "resolution_rate": round(
            len(resolved_v) / max(len(violations), 1) * 100, 1
        ),
    }
