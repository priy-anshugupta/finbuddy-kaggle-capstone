"""
Agent Service for managing agent interactions
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.core.logging import get_logger
from app.core.redis import CacheService
from app.models import Conversation, Message, AgentState

from agents.orchestrators import (
    MoneyManagementOrchestrator,
    InvestmentOrchestrator,
    FinancialProductsOrchestrator
)


logger = get_logger(__name__)


class AgentService:
    """
    Service for managing agent interactions and routing.
    
    Routes requests to appropriate orchestrators based on intent.
    """
    
    # Intent to orchestrator mapping
    INTENT_ROUTING = {
        # Money Management (Orchestrator 1)
        "spending": "money_management",
        "budget": "money_management",
        "transaction": "money_management",
        "expense": "money_management",
        "savings": "money_management",
        "ocr": "money_management",
        "categorize": "money_management",
        
        # Investment (Orchestrator 2)
        "invest": "investment",
        "stock": "investment",
        "mutual_fund": "investment",
        "portfolio": "investment",
        "sip": "investment",
        "market": "investment",
        "nifty": "investment",
        "sensex": "investment",
        
        # Financial Products (Orchestrator 3)
        "credit_card": "financial_products",
        "loan": "financial_products",
        "emi": "financial_products",
        "tax": "financial_products",
        "itr": "financial_products",
    }
    
    def __init__(
        self,
        db: AsyncSession,
        cache: Optional[CacheService] = None
    ):
        self.db = db
        self.cache = cache
        
        # Lazy load orchestrators
        self._money_orchestrator = None
        self._investment_orchestrator = None
        self._products_orchestrator = None
    
    @property
    def money_orchestrator(self):
        if self._money_orchestrator is None:
            self._money_orchestrator = MoneyManagementOrchestrator()
        return self._money_orchestrator
    
    @property
    def investment_orchestrator(self):
        if self._investment_orchestrator is None:
            self._investment_orchestrator = InvestmentOrchestrator()
        return self._investment_orchestrator
    
    @property
    def products_orchestrator(self):
        if self._products_orchestrator is None:
            self._products_orchestrator = FinancialProductsOrchestrator()
        return self._products_orchestrator
    
    def detect_intent(self, message: str) -> str:
        """
        Detect intent from user message.
        
        Args:
            message: User message
            
        Returns:
            Detected intent
        """
        message_lower = message.lower()
        
        for keyword, orchestrator in self.INTENT_ROUTING.items():
            if keyword in message_lower:
                return orchestrator
        
        # Default to money management for general queries
        return "money_management"
    
    async def process_message(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent system.
        
        Args:
            user_id: User ID
            conversation_id: Conversation ID
            message: User message
            context: Additional context
            
        Returns:
            Agent response
        """
        start_time = datetime.utcnow()
        
        # Detect intent and select orchestrator
        intent = self.detect_intent(message)
        
        logger.info(
            "Processing message",
            user_id=user_id,
            intent=intent,
            message_length=len(message)
        )
        
        # Build context
        full_context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": start_time.isoformat(),
            **(context or {})
        }
        
        # Add user data to context
        user_data = await self._get_user_context(user_id)
        if user_data:
            full_context["user_data"] = user_data
        
        # Route to appropriate orchestrator
        try:
            if intent == "money_management":
                result = await self.money_orchestrator.run(message, full_context)
            elif intent == "investment":
                result = await self.investment_orchestrator.run(message, full_context)
            elif intent == "financial_products":
                result = await self.products_orchestrator.run(message, full_context)
            else:
                result = await self.money_orchestrator.run(message, full_context)
            
            # Log response time
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Save to conversation
            await self._save_message(
                conversation_id=conversation_id,
                role="user",
                content=message
            )
            
            await self._save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=result.get("output", ""),
                metadata={
                    "intent": intent,
                    "orchestrator": intent,
                    "duration_ms": duration_ms
                }
            )
            
            return {
                "success": True,
                "response": result.get("output", ""),
                "intent": intent,
                "orchestrator": intent,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(
                "Agent processing failed",
                error=str(e),
                user_id=user_id
            )
            return {
                "success": False,
                "error": str(e),
                "intent": intent
            }
    
    async def stream_response(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Stream agent response.
        
        Yields response chunks as they're generated.
        """
        intent = self.detect_intent(message)
        
        full_context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(context or {})
        }
        
        try:
            if intent == "money_management":
                orchestrator = self.money_orchestrator
            elif intent == "investment":
                orchestrator = self.investment_orchestrator
            else:
                orchestrator = self.products_orchestrator
            
            full_response = ""
            
            async for chunk in orchestrator.stream(message, full_context):
                yield chunk
                full_response += chunk.get("content", "")
            
            # Save complete response
            await self._save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                metadata={"intent": intent, "streamed": True}
            )
            
        except Exception as e:
            yield {"type": "error", "content": str(e)}
    
    async def _get_user_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data for context."""
        if self.cache:
            cached = await self.cache.get_json(f"user_context:{user_id}")
            if cached:
                return cached
        
        # Would fetch from database
        return None
    
    async def _save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Save message to database."""
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            self.db.add(message)
            await self.db.commit()
        except Exception as e:
            logger.error("Failed to save message", error=str(e))
            await self.db.rollback()
    
    async def get_agent_state(
        self,
        user_id: str,
        orchestrator: str
    ) -> Optional[Dict[str, Any]]:
        """Get saved agent state for user."""
        result = await self.db.execute(
            select(AgentState).where(
                AgentState.user_id == user_id,
                AgentState.orchestrator == orchestrator,
                AgentState.is_active == True
            )
        )
        state = result.scalar_one_or_none()
        return state.context if state else None
    
    async def save_agent_state(
        self,
        user_id: str,
        orchestrator: str,
        state_data: Dict[str, Any]
    ):
        """Save agent state."""
        # Check for existing state
        result = await self.db.execute(
            select(AgentState).where(
                AgentState.user_id == user_id,
                AgentState.orchestrator == orchestrator
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.context = state_data
            existing.updated_at = datetime.utcnow()
        else:
            state = AgentState(
                user_id=user_id,
                orchestrator=orchestrator,
                context=state_data,
                is_active=True
            )
            self.db.add(state)
        
        await self.db.commit()
