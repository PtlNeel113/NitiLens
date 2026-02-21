"""
NitiGuard AI — Agent API Routes
POST /api/agent/chat — main chat endpoint
GET /api/agent/history/{conversation_id} — conversation history
POST /api/agent/action — action mode with confirmation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.database import get_db
from app.auth import get_current_active_user
from app.models.db_models import User, AgentConversation
from agent.agent_controller import AgentController

router = APIRouter(prefix="/api/agent", tags=["Agent"])


# --- Request/Response Models ---

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    is_voice: bool = False


class ChatResponse(BaseModel):
    reply: str
    sources: List[Dict[str, Any]] = []
    risk_references: List[Dict[str, Any]] = []
    related_violations: List[Dict[str, Any]] = []
    conversation_id: str
    intent: str


class ActionRequest(BaseModel):
    message: str
    action_type: str
    target_id: str
    conversation_id: str
    confirmed: bool = False


class ActionResponse(BaseModel):
    reply: str
    action_required: bool = False
    action_type: Optional[str] = None
    target_id: Optional[str] = None
    success: Optional[bool] = None
    conversation_id: str


class ConversationMessage(BaseModel):
    message: str
    response: str
    intent: Optional[str]
    timestamp: datetime


# --- Endpoints ---

@router.post("/chat", response_model=ChatResponse)
async def agent_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Main NitiGuard AI chat endpoint.
    Processes user message through intent classification, context building,
    LLM generation, and returns a data-grounded response.
    """
    controller = AgentController(db, current_user)
    
    try:
        result = await controller.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            is_voice=request.is_voice
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        print(f"Agent chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your message. Please try again."
        )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get conversation history for a specific conversation"""
    messages = db.query(AgentConversation).filter(
        AgentConversation.conversation_id == conversation_id,
        AgentConversation.org_id == current_user.org_id
    ).order_by(AgentConversation.timestamp.asc()).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "message": msg.message,
                "response": msg.response,
                "intent": msg.intent,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
    }


@router.post("/action", response_model=ActionResponse)
async def agent_action(
    request: ActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Agent action mode — execute actions with confirmation.
    First call returns confirmation prompt. Second call with confirmed=True executes.
    """
    controller = AgentController(db, current_user)
    
    if request.confirmed:
        # Execute the action
        result = controller.execute_action(request.action_type, request.target_id)
        return ActionResponse(
            reply=result["message"],
            success=result["success"],
            action_required=False,
            conversation_id=request.conversation_id
        )
    else:
        # Request confirmation
        result = await controller.handle_action_request(
            message=request.message,
            action_type=request.action_type,
            target_id=request.target_id,
            conversation_id=request.conversation_id
        )
        return ActionResponse(**result)
