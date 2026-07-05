"""
Google ADK Service Integration

Provides a service-layer wrapper around the ADKOrchestrator so that
existing FastAPI endpoints can easily switch between LangChain (legacy)
and ADK (course-compliant) backends via the AGENT_FRAMEWORK setting.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ADKAgentService:
    """
    Service facade for ADK-based agent interactions.

    This mirrors the interface of the legacy AgentService so that
    FastAPI routes can transparently use either backend.
    """

    def __init__(self, db=None, cache=None):
        self.db = db
        self.cache = cache
        self._orchestrator = None

    @property
    def orchestrator(self):
        """Lazy-load the ADK orchestrator."""
        if self._orchestrator is None:
            from google_adk.root_agent import ADKOrchestrator
            self._orchestrator = ADKOrchestrator()
        return self._orchestrator

    async def process_message(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message through the ADK agent system.

        Args:
            user_id: User ID
            conversation_id: Conversation ID (used as ADK session ID)
            message: User message
            context: Additional context (ignored by ADK runner, but logged)

        Returns:
            Standardized response dict compatible with legacy format.
        """
        start_time = datetime.utcnow()

        logger.info(
            "ADK processing message",
            user_id=user_id,
            conversation_id=conversation_id,
            message_length=len(message),
        )

        try:
            result = await self.orchestrator.run(
                user_message=message,
                session_id=conversation_id,
            )

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            return {
                "success": result.get("success", False),
                "response": result.get("output", ""),
                "intent": "adk_orchestrated",
                "orchestrator": "adk_root",
                "duration_ms": duration_ms,
                "session_id": result.get("session_id"),
                "framework": "google_adk",
            }
        except Exception as e:
            logger.error("ADK processing failed", error=str(e), user_id=user_id)
            return {
                "success": False,
                "error": str(e),
                "intent": "unknown",
                "framework": "google_adk",
            }

    async def stream_response(
        self,
        user_id: str,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Stream agent response via ADK (fallback to full response for now).

        ADK's async runner yields events; we map them to SSE-compatible chunks.
        """
        start_time = datetime.utcnow()

        try:
            result = await self.orchestrator.run(
                user_message=message,
                session_id=conversation_id,
            )

            output = result.get("output", "")
            # Yield the full output as a single chunk for simplicity
            # In production, split by sentence/paragraph for true streaming
            yield {
                "type": "content",
                "agent_name": "finbuddy_root",
                "content": output,
                "framework": "google_adk",
            }

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            yield {
                "type": "metadata",
                "duration_ms": duration_ms,
                "framework": "google_adk",
            }

        except Exception as e:
            yield {"type": "error", "content": str(e), "framework": "google_adk"}


def get_agent_service(db=None, cache=None):
    """
    Factory that returns the appropriate agent service based on config.

    Returns:
        ADKAgentService if AGENT_FRAMEWORK == "adk", else legacy AgentService.
    """
    if settings.AGENT_FRAMEWORK == "adk":
        logger.info("Using Google ADK agent service")
        return ADKAgentService(db=db, cache=cache)
    else:
        logger.info("Using legacy LangChain agent service")
        from app.services.agent_service import AgentService
        return AgentService(db=db, cache=cache)
