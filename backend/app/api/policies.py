"""
API routes for policy management and rule review.
"""
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.pdf_parser import extract_text_from_pdf
from app.core.rule_engine import (
    add_rules, approve_rule, delete_rule, get_rules, update_rule
)
from app.core.rule_extractor import extract_rules_from_text
from app.models.rule import PolicyRule

router = APIRouter(prefix="/api/policies", tags=["Policies"])

# In-memory policy registry (lightweight — no DB needed for hackathon)
_POLICIES_FILE = Path(__file__).parent.parent / "storage" / "policies.json"


def _load_policies() -> list:
    try:
        return json.loads(_POLICIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_policies(policies: list) -> None:
    _POLICIES_FILE.write_text(json.dumps(policies, indent=2), encoding="utf-8")


@router.get("", summary="List all uploaded policies")
def list_policies():
    return _load_policies()


@router.post("/upload", summary="Upload a policy PDF and extract rules")
async def upload_policy(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    policy_id = f"pol-{uuid.uuid4().hex[:8]}"

    # Save temp file for parsing
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text_from_pdf(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    extracted = extract_rules_from_text(text, policy_id, file.filename)
    added = add_rules(extracted)

    policy_record = {
        "id": policy_id,
        "name": file.filename,
        "uploaded_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "rules_extracted": len(added),
        "file_size_kb": round(file.size / 1024, 1) if file.size else 0,
    }
    policies = _load_policies()
    policies.append(policy_record)
    _save_policies(policies)

    return {
        "policy": policy_record,
        "extracted_rules": [r.model_dump() for r in added],
        "message": f"Extracted {len(added)} rules from '{file.filename}'. Rules require approval before scanning.",
    }


@router.get("/{policy_id}/rules", summary="List rules for a specific policy")
def get_policy_rules(policy_id: str):
    rules = [r for r in get_rules() if r.policy_id == policy_id]
    return rules


@router.get("/rules/all", summary="List all rules across all policies")
def list_all_rules(approved_only: bool = False):
    return get_rules(approved_only=approved_only)


@router.put("/rules/{rule_id}/approve", summary="Approve or reject a rule")
def toggle_rule_approval(rule_id: str, approved: bool = True):
    rule = approve_rule(rule_id, approved)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/rules/{rule_id}", summary="Update a rule's fields")
def modify_rule(rule_id: str, updates: dict):
    rule = update_rule(rule_id, updates)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/rules/{rule_id}", summary="Delete a rule")
def remove_rule(rule_id: str):
    if not delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"deleted": rule_id}
