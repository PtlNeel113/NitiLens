"""
NitiGuard AI — LLM Client
Google Gemini integration with timeouts, rate limiting, and graceful fallback
"""
import os
import time
import asyncio
from typing import Optional, List, Dict, Any
from collections import defaultdict
from datetime import datetime

# Try to import google generativeai, provide fallback
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class RateLimiter:
    """Simple in-memory rate limiter per user"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old entries
        self._requests[user_id] = [
            t for t in self._requests[user_id] if t > window_start
        ]
        
        if len(self._requests[user_id]) >= self.max_requests:
            return False
        
        self._requests[user_id].append(now)
        return True


class LLMClient:
    """LLM client for NitiGuard AI using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY") or os.getenv("TRANSLATION_API_KEY", "")
        self.timeout_seconds = 10
        self.max_tokens = 1024
        self.rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
        self._initialized = False
        self._model = None
    
    def _initialize(self):
        """Lazy initialization of Gemini client"""
        if self._initialized:
            return
        
        if not GENAI_AVAILABLE:
            print("⚠️ google-generativeai not installed. LLM features disabled.")
            self._initialized = True
            return
        
        if not self.api_key:
            print("⚠️ No LLM API key configured. Set LLM_API_KEY in .env")
            self._initialized = True
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel("gemini-pro")
            self._initialized = True
            print("✅ Gemini LLM client initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize Gemini: {e}")
            self._initialized = True
    
    async def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_id: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Returns:
            {
                "text": str,
                "success": bool,
                "error": Optional[str],
                "tokens_used": int
            }
        """
        # Rate limit check
        if user_id and not self.rate_limiter.is_allowed(user_id):
            return {
                "text": "You're sending messages too quickly. Please wait a moment before trying again.",
                "success": False,
                "error": "rate_limited",
                "tokens_used": 0
            }
        
        self._initialize()
        
        if not self._model:
            return self._fallback_response(system_prompt, user_prompt)
        
        # Build conversation with history
        full_prompt = f"{system_prompt}\n\n"
        
        if history:
            for msg in history[-5:]:  # Last 5 messages only
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    full_prompt += f"User: {content}\n"
                else:
                    full_prompt += f"Assistant: {content}\n"
            full_prompt += "\n"
        
        full_prompt += user_prompt
        
        try:
            # Run with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self._model.generate_content,
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.max_tokens,
                        temperature=0.3,  # Low temperature for factual compliance answers
                    )
                ),
                timeout=self.timeout_seconds
            )
            
            text = response.text if response.text else "I couldn't generate a response. Please try rephrasing your question."
            
            return {
                "text": text,
                "success": True,
                "error": None,
                "tokens_used": len(text.split())  # Approximate
            }
            
        except asyncio.TimeoutError:
            return {
                "text": "Response timed out. The system is experiencing high load. Please try again.",
                "success": False,
                "error": "timeout",
                "tokens_used": 0
            }
        except Exception as e:
            print(f"LLM error: {e}")
            return self._fallback_response(system_prompt, user_prompt)
    
    async def classify_intent(self, message: str) -> str:
        """
        Classify user intent using keyword matching first, then LLM fallback.
        
        Returns one of:
            risk_inquiry, violation_explanation, policy_clarification,
            remediation_status, trend_summary, audit_summary,
            action_request, general_help
        """
        # Keyword-based classification (fast path)
        message_lower = message.lower()
        
        keyword_map = {
            "risk_inquiry": [
                "risk", "risk score", "risk level", "compliance status",
                "how safe", "how risky", "overall risk", "risk assessment"
            ],
            "violation_explanation": [
                "violation", "flagged", "why was", "explain violation",
                "transaction", "tx-", "violated", "breach", "non-compliant"
            ],
            "policy_clarification": [
                "policy", "rule", "regulation", "requirement", "guideline",
                "section", "framework", "what does the policy", "policy say"
            ],
            "remediation_status": [
                "remediation", "fix", "resolve", "open case", "pending case",
                "overdue", "assigned", "remediate", "action plan"
            ],
            "trend_summary": [
                "trend", "over time", "change", "compared to", "last week",
                "last month", "increasing", "decreasing", "getting worse",
                "getting better", "progress", "historical"
            ],
            "audit_summary": [
                "audit", "summary", "report", "scan result", "last scan",
                "generate report", "overview", "summarize", "scan summary"
            ],
            "action_request": [
                "mark as", "update", "change status", "assign", "close",
                "review", "mark reviewed", "resolve violation", "dismiss"
            ],
        }
        
        best_match = "general_help"
        best_score = 0
        
        for intent, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > best_score:
                best_score = score
                best_match = intent
        
        if best_score >= 1:
            return best_match
        
        # LLM fallback for ambiguous messages
        if self._model:
            try:
                from agent.prompts import INTENT_CLASSIFIER_PROMPT
                prompt = INTENT_CLASSIFIER_PROMPT.format(message=message)
                
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._model.generate_content,
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=20,
                            temperature=0.1,
                        )
                    ),
                    timeout=5
                )
                
                intent = response.text.strip().lower().replace(" ", "_")
                valid_intents = list(keyword_map.keys()) + ["general_help"]
                
                if intent in valid_intents:
                    return intent
            except Exception:
                pass
        
        return best_match
    
    def _fallback_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Provide a structured fallback when LLM is unavailable.
        Extracts data from the context and formats it directly.
        """
        # Try to extract context data from the prompt
        lines = user_prompt.split("\n")
        context_lines = []
        in_context = False
        
        for line in lines:
            if "SYSTEM CONTEXT:" in line or "CURRENT SYSTEM STATUS:" in line:
                in_context = True
                continue
            if "USER QUESTION:" in line:
                in_context = False
                continue
            if in_context and line.strip().startswith("- "):
                context_lines.append(line.strip())
        
        if context_lines:
            formatted = "Based on current system data:\n\n" + "\n".join(context_lines)
            formatted += "\n\n*Note: AI analysis is currently unavailable. Showing raw system data.*"
        else:
            formatted = (
                "I'm currently unable to process your request with full AI analysis. "
                "The compliance data is available through the dashboard. "
                "Please check the relevant section or try again later."
            )
        
        return {
            "text": formatted,
            "success": True,
            "error": "llm_unavailable",
            "tokens_used": 0
        }


# Singleton instance
llm_client = LLMClient()
