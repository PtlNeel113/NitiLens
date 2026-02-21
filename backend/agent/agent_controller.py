"""
NitiGuard AI — Agent Controller
Main orchestrator: intent detection → context building → LLM call → response formatting
"""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.db_models import (
    User, UserRole, Violation, ViolationStatus, AgentConversation
)
from agent.context_builder import ContextBuilder
from agent.llm_client import llm_client
from agent.voice_processor import voice_processor
from agent.prompts import (
    SYSTEM_PROMPT, build_user_prompt, build_action_confirmation_prompt
)


class AgentController:
    """
    Main orchestrator for NitiGuard AI.
    Pipeline: classify intent → build context → call LLM → format response → persist
    """
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.context_builder = ContextBuilder(db, user)
    
    async def process_message(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        is_voice: bool = False
    ) -> Dict[str, Any]:
        """
        Process a user message through the full agent pipeline.
        
        Returns:
            {
                "reply": str,
                "sources": List[Dict],
                "risk_references": List[Dict],
                "related_violations": List[Dict],
                "conversation_id": str,
                "intent": str
            }
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Normalize voice input
        if is_voice:
            message = voice_processor.normalize_voice_input(message)
        
        # Step 1: Classify intent
        intent = await llm_client.classify_intent(message)
        
        # Step 2: Build context from database
        context_data = self._build_context(intent, message)
        
        # Step 3: Check for errors in context
        if "error" in context_data:
            reply = context_data["error"]
            sources = []
            risk_refs = []
            violations = []
        else:
            # Step 4: Build prompt and call LLM
            user_prompt = build_user_prompt(intent, context_data, message)
            
            # Get conversation history
            history = self._get_conversation_history(conversation_id)
            
            # Build role-aware system prompt
            system_prompt = self._build_system_prompt()
            
            # Call LLM
            llm_response = await llm_client.generate_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                history=history,
                user_id=str(self.user.user_id)
            )
            
            reply = llm_response["text"]
            
            # Step 5: Extract sources and references
            sources = self.context_builder.get_sources(intent, context_data)
            risk_refs = self._get_risk_references(intent, context_data)
            violations = self._get_related_violations(intent, message)
        
        # Step 6: Persist conversation
        self._save_conversation(conversation_id, message, reply, intent)
        
        return {
            "reply": reply,
            "sources": sources,
            "risk_references": risk_refs,
            "related_violations": violations,
            "conversation_id": conversation_id,
            "intent": intent,
        }
    
    async def handle_action_request(
        self,
        message: str,
        action_type: str,
        target_id: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Handle action requests (e.g., 'mark violation as reviewed').
        Requires confirmation before executing.
        """
        # Check permissions
        if self.user.role == UserRole.VIEWER:
            return {
                "reply": "You don't have permission to perform actions. Contact your Compliance Admin.",
                "action_required": False,
                "conversation_id": conversation_id,
            }
        
        # Build confirmation prompt
        action_details = {
            "action_type": action_type,
            "target_id": target_id,
            "requested_by": self.user.full_name or self.user.email,
            "role": self.user.role.value,
        }
        
        confirmation_prompt = build_action_confirmation_prompt(action_type, action_details)
        
        llm_response = await llm_client.generate_response(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=confirmation_prompt,
            user_id=str(self.user.user_id)
        )
        
        return {
            "reply": llm_response["text"],
            "action_required": True,
            "action_type": action_type,
            "target_id": target_id,
            "conversation_id": conversation_id,
        }
    
    def execute_action(self, action_type: str, target_id: str) -> Dict[str, Any]:
        """Execute a confirmed action"""
        if self.user.role == UserRole.VIEWER:
            return {"success": False, "message": "Insufficient permissions"}
        
        try:
            if action_type == "mark_reviewed":
                violation = self.db.query(Violation).filter(
                    Violation.org_id == self.user.org_id,
                    Violation.violation_id == target_id
                ).first()
                
                if not violation:
                    return {"success": False, "message": "Violation not found"}
                
                violation.status = ViolationStatus.REVIEWED
                violation.reviewed_at = datetime.utcnow()
                violation.reviewed_by = self.user.user_id
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Violation {str(target_id)[:8]} marked as reviewed."
                }
            
            return {"success": False, "message": f"Unknown action: {action_type}"}
            
        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"Action failed: {str(e)}"}
    
    def _build_context(self, intent: str, message: str) -> Dict[str, Any]:
        """Build context based on detected intent"""
        try:
            if intent == "risk_inquiry":
                return self.context_builder.build_risk_context()
            elif intent == "violation_explanation":
                return self.context_builder.build_violation_context(message)
            elif intent == "policy_clarification":
                return self.context_builder.build_policy_context(message)
            elif intent == "remediation_status":
                return self.context_builder.build_remediation_context()
            elif intent == "trend_summary":
                return self.context_builder.build_trend_context()
            elif intent == "audit_summary":
                return self.context_builder.build_audit_context()
            elif intent == "action_request":
                return self.context_builder.build_general_context()
            else:
                return self.context_builder.build_general_context()
        except Exception as e:
            print(f"Context build error: {e}")
            return self.context_builder.build_general_context()
    
    def _build_system_prompt(self) -> str:
        """Build role-aware system prompt"""
        prompt = SYSTEM_PROMPT
        
        if self.user.role == UserRole.VIEWER:
            prompt += "\n\nROLE RESTRICTION: This user is a Viewer. Do NOT expose financial details, transaction amounts, or sensitive operational data."
        elif self.user.role in [UserRole.SUPER_ADMIN, UserRole.COMPLIANCE_ADMIN]:
            prompt += "\n\nROLE: This user has full compliance admin access. Provide detailed and complete information."
        
        return prompt
    
    def _get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get last 5 messages from conversation history"""
        messages = self.db.query(AgentConversation).filter(
            AgentConversation.conversation_id == conversation_id,
            AgentConversation.org_id == self.user.org_id
        ).order_by(AgentConversation.timestamp.desc()).limit(5).all()
        
        history = []
        for msg in reversed(messages):
            history.append({"role": "user", "content": msg.message})
            if msg.response:
                history.append({"role": "assistant", "content": msg.response})
        
        return history
    
    def _save_conversation(
        self,
        conversation_id: str,
        message: str,
        response: str,
        intent: str
    ):
        """Persist conversation to database"""
        try:
            conversation = AgentConversation(
                conversation_id=conversation_id,
                org_id=self.user.org_id,
                user_id=self.user.user_id,
                role=self.user.role.value,
                message=message,
                response=response,
                intent=intent,
                timestamp=datetime.utcnow()
            )
            self.db.add(conversation)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Failed to save conversation: {e}")
    
    def _get_risk_references(self, intent: str, context_data: Dict) -> List[Dict]:
        """Get risk-related references for the response"""
        refs = []
        
        if intent in ["risk_inquiry", "trend_summary"]:
            risk_score = context_data.get("risk_score", 0)
            refs.append({
                "metric": "risk_score",
                "value": risk_score,
                "level": context_data.get("risk_level", "Unknown"),
            })
        
        if "critical_violations" in context_data and context_data["critical_violations"] > 0:
            refs.append({
                "metric": "critical_violations",
                "value": context_data["critical_violations"],
                "level": "Critical",
            })
        
        return refs
    
    def _get_related_violations(self, intent: str, message: str) -> List[Dict]:
        """Get related violations for the response"""
        if intent not in ["violation_explanation", "risk_inquiry", "audit_summary"]:
            return []
        
        violations = self.db.query(Violation).filter(
            Violation.org_id == self.user.org_id,
            Violation.status == ViolationStatus.PENDING
        ).order_by(Violation.final_risk_score.desc()).limit(3).all()
        
        return [
            {
                "id": str(v.violation_id)[:8],
                "severity": v.severity or "unknown",
                "field": v.field_name or "N/A",
                "score": v.final_risk_score or 0,
            }
            for v in violations
        ]
