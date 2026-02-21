"""
Remediation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.db_models import (
    RemediationCase, RemediationComment, RemediationStatus, RemediationPriority, User
)
from app.auth import get_current_active_user
from app.services.remediation_engine import RemediationEngine
from app.middleware.subscription_middleware import require_feature

router = APIRouter(prefix="/api/remediation", tags=["Remediation"])


class CaseResponse(BaseModel):
    case_id: str
    violation_id: str
    assigned_to: Optional[str]
    assigned_to_name: Optional[str]
    status: str
    priority: str
    recommended_action: str
    due_date: str
    created_at: str
    updated_at: str
    completed_at: Optional[str]


class UpdateStatusRequest(BaseModel):
    status: str
    comment: Optional[str] = None


class AssignRequest(BaseModel):
    user_id: str


class CommentRequest(BaseModel):
    comment_text: str


@router.get("/", response_model=List[CaseResponse])
def get_remediation_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Get remediation cases with filters"""
    engine = RemediationEngine(db)
    
    # Parse filters
    status_filter = RemediationStatus(status) if status else None
    priority_filter = RemediationPriority(priority) if priority else None
    assigned_filter = UUID(assigned_to) if assigned_to else None
    
    cases = engine.get_cases(
        org_id=current_user.org_id,
        status=status_filter,
        priority=priority_filter,
        assigned_to=assigned_filter
    )
    
    # Format response
    result = []
    for case in cases:
        assigned_user = db.query(User).filter(User.user_id == case.assigned_to).first()
        
        result.append({
            "case_id": str(case.case_id),
            "violation_id": str(case.violation_id),
            "assigned_to": str(case.assigned_to) if case.assigned_to else None,
            "assigned_to_name": assigned_user.full_name if assigned_user else None,
            "status": case.status.value,
            "priority": case.priority.value,
            "recommended_action": case.recommended_action,
            "due_date": case.due_date.isoformat(),
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat(),
            "completed_at": case.completed_at.isoformat() if case.completed_at else None
        })
    
    return result


@router.get("/{case_id}")
def get_case_details(
    case_id: UUID,
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Get detailed case information including comments"""
    case = db.query(RemediationCase).filter(
        RemediationCase.case_id == case_id,
        RemediationCase.org_id == current_user.org_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get comments
    comments = db.query(RemediationComment).filter(
        RemediationComment.case_id == case_id
    ).order_by(RemediationComment.created_at.desc()).all()
    
    # Get assigned user
    assigned_user = db.query(User).filter(User.user_id == case.assigned_to).first()
    
    return {
        "case_id": str(case.case_id),
        "violation_id": str(case.violation_id),
        "rule_id": str(case.rule_id),
        "assigned_to": str(case.assigned_to) if case.assigned_to else None,
        "assigned_to_name": assigned_user.full_name if assigned_user else None,
        "status": case.status.value,
        "priority": case.priority.value,
        "recommended_action": case.recommended_action,
        "due_date": case.due_date.isoformat(),
        "created_at": case.created_at.isoformat(),
        "updated_at": case.updated_at.isoformat(),
        "completed_at": case.completed_at.isoformat() if case.completed_at else None,
        "comments": [
            {
                "comment_id": str(c.comment_id),
                "user_id": str(c.user_id),
                "user_name": db.query(User).filter(User.user_id == c.user_id).first().full_name,
                "comment_text": c.comment_text,
                "created_at": c.created_at.isoformat()
            }
            for c in comments
        ]
    }


@router.post("/update-status/{case_id}")
async def update_case_status(
    case_id: UUID,
    request: UpdateStatusRequest,
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Update case status"""
    engine = RemediationEngine(db)
    
    try:
        status = RemediationStatus(request.status)
        case = engine.update_case_status(
            case_id=case_id,
            status=status,
            user_id=current_user.user_id,
            comment=request.comment
        )
        
        return {
            "message": "Status updated successfully",
            "case_id": str(case.case_id),
            "new_status": case.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/comment/{case_id}")
def add_comment(
    case_id: UUID,
    request: CommentRequest,
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Add comment to case"""
    case = db.query(RemediationCase).filter(
        RemediationCase.case_id == case_id,
        RemediationCase.org_id == current_user.org_id
    ).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    comment = RemediationComment(
        case_id=case_id,
        user_id=current_user.user_id,
        comment_text=request.comment_text
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        "message": "Comment added successfully",
        "comment_id": str(comment.comment_id),
        "created_at": comment.created_at.isoformat()
    }


@router.post("/assign/{case_id}")
def reassign_case(
    case_id: UUID,
    request: AssignRequest,
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Reassign case to different user"""
    engine = RemediationEngine(db)
    
    try:
        new_user_id = UUID(request.user_id)
        case = engine.reassign_case(
            case_id=case_id,
            new_user_id=new_user_id,
            reassigned_by=current_user.user_id
        )
        
        return {
            "message": "Case reassigned successfully",
            "case_id": str(case.case_id),
            "assigned_to": str(case.assigned_to)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary")
def get_remediation_stats(
    current_user: User = Depends(require_feature("remediation")),
    db: Session = Depends(get_db)
):
    """Get remediation statistics"""
    engine = RemediationEngine(db)
    stats = engine.get_case_statistics(current_user.org_id)
    
    return stats
