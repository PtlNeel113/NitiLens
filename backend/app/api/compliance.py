"""
API routes for compliance scanning and violation retrieval.
"""
from typing import List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query
from app.core.violation_engine import (
    get_dataset_stats, load_violations, run_scan
)
from app.core.scheduler import get_scheduler_status
from app.models.violation import Violation

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.post("/scan", summary="Run a compliance scan on the IBM AML dataset")
def trigger_scan():
    """
    Runs all approved rules against the IBM AML transaction dataset.
    Returns a summary of violations found.
    """
    try:
        violations = run_scan()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}")

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    rule_counts: dict = {}

    for v in violations:
        severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1
        rule_counts[v.rule_id] = rule_counts.get(v.rule_id, 0) + 1

    return {
        "total_violations": len(violations),
        "severity_breakdown": severity_counts,
        "violations_by_rule": rule_counts,
        "message": f"Scan complete. {len(violations)} violation(s) detected and saved.",
    }


@router.get("/violations", summary="List all compliance violations")
def list_violations(
    status: Optional[Literal["open", "reviewed", "resolved", "false_positive"]] = None,
    severity: Optional[Literal["critical", "high", "medium", "low"]] = None,
    rule_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    violations = load_violations()

    if status:
        violations = [v for v in violations if v.status == status]
    if severity:
        violations = [v for v in violations if v.severity == severity]
    if rule_id:
        violations = [v for v in violations if v.rule_id == rule_id]

    total = len(violations)
    paginated = violations[offset: offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "violations": [v.model_dump() for v in paginated],
    }


@router.get("/violations/{violation_id}", summary="Get a single violation by ID")
def get_violation(violation_id: str):
    violations = load_violations()
    match = next((v for v in violations if v.id == violation_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Violation not found")
    return match


@router.get("/summary", summary="High-level compliance summary statistics")
def compliance_summary():
    violations = load_violations()
    stats = get_dataset_stats()

    total_txns = stats.get("total_transactions", 0)
    open_v = [v for v in violations if v.status == "open"]
    resolved_v = [v for v in violations if v.status == "resolved"]
    false_pos = [v for v in violations if v.status == "false_positive"]

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in open_v:
        severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

    compliance_rate = round((1 - len(open_v) / max(total_txns, 1)) * 100, 2)

    return {
        "total_transactions_scanned": total_txns,
        "total_violations": len(violations),
        "open_violations": len(open_v),
        "resolved_violations": len(resolved_v),
        "false_positives": len(false_pos),
        "compliance_rate": compliance_rate,
        "severity_breakdown": severity_counts,
        "dataset_laundering_rate": stats.get("laundering_percentage", 0),
    }


@router.get("/scheduler", summary="Get periodic scan scheduler status")
def scheduler_status():
    return get_scheduler_status()
