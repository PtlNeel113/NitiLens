"""
API routes for policy management and rule review.
"""
import json
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.services.document_parser import extract_text, get_document_metadata
from app.core.rule_engine import (
    add_rules, approve_rule, delete_rule, get_rules, update_rule
)
from app.core.rule_extractor import extract_rules_from_text
from app.models.rule import PolicyRule
from app.database import get_db
from app.models.db_models import User
from app.auth import get_current_active_user
from app.middleware.subscription_middleware import check_policy_limit
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/api/policies", tags=["Policies"])

# In-memory policy registry (lightweight — no DB needed for hackathon)
_POLICIES_FILE = Path(__file__).parent.parent / "storage" / "policies.json"

# Allowed extensions and their MIME types
_ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}
_ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}


def _load_policies() -> list:
    try:
        return json.loads(_POLICIES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_policies(policies: list) -> None:
    _POLICIES_FILE.write_text(json.dumps(policies, indent=2), encoding="utf-8")


def _detect_file_type(filename: str) -> Optional[str]:
    """Return normalized file type from filename extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    elif ext in (".ppt", ".pptx"):
        return ext.lstrip(".")
    return None


@router.get("", summary="List all uploaded policies")
def list_policies():
    return _load_policies()


@router.post("/upload", summary="Upload a policy document (PDF or PPT/PPTX) and extract rules")
async def upload_policy(
    file: UploadFile = File(...),
    current_user: User = Depends(check_policy_limit),
    db: Session = Depends(get_db)
):
    # ── Validate file type ──────────────────────────────────────
    file_type = _detect_file_type(file.filename or "")
    if file_type is None:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Unsupported file type. Please upload PDF or PPTX.",
            },
        )

    policy_id = f"pol-{uuid.uuid4().hex[:8]}"

    # Increment policy usage counter
    service = SubscriptionService(db)
    service.increment_policy_usage(current_user.org_id)

    # ── Save temp file for parsing ──────────────────────────────
    suffix = Path(file.filename or "upload").suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    # ── Extract text with timeout protection ────────────────────
    try:
        text = extract_text(tmp_path, file_type)
        metadata = get_document_metadata(tmp_path, file_type)
    except TimeoutError:
        Path(tmp_path).unlink(missing_ok=True)
        return JSONResponse(
            status_code=408,
            content={
                "status": "error",
                "message": "Document processing timed out.",
            },
        )
    except ValueError as ve:
        Path(tmp_path).unlink(missing_ok=True)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(ve),
            },
        )
    except Exception as exc:
        Path(tmp_path).unlink(missing_ok=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to process document: {exc}",
            },
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # ── Extract rules (unchanged engine) ────────────────────────
    extracted = extract_rules_from_text(text, policy_id, file.filename)
    added = add_rules(extracted)

    # ── Build descriptive info string ───────────────────────────
    if file_type == "pdf":
        pages = metadata.get("total_pages", "?")
        doc_info = f"Found {pages} pages"
    else:
        slides = metadata.get("total_slides", "?")
        doc_info = f"Found {slides} slides"

    extracted_char_count = len(text)

    policy_record = {
        "id": policy_id,
        "name": file.filename,
        "uploaded_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "rules_extracted": len(added),
        "file_size_kb": round(file.size / 1024, 1) if file.size else 0,
        "file_type": file_type,
        "total_pages": metadata.get("total_pages"),
        "total_slides": metadata.get("total_slides"),
        "extracted_char_count": extracted_char_count,
    }
    policies = _load_policies()
    policies.append(policy_record)
    _save_policies(policies)

    return {
        "policy": policy_record,
        "extracted_rules": [r.model_dump() for r in added],
        "doc_info": doc_info,
        "message": f"Extracted {len(added)} rules from '{file.filename}'. {doc_info}. Rules require approval before scanning.",
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
