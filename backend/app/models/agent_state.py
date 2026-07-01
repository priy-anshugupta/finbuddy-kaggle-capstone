"""
Agent state and memory persistence models
"""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class AgentState(Base):
    """Persist agent conversation state and memory."""
    
    __tablename__ = "agent_states"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True
    )
    
    # Agent Identity
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    orchestrator: Mapped[str] = mapped_column(String(100))  # orchestrator_1, orchestrator_2, orchestrator_3
    
    # State Data
    state_data: Mapped[dict] = mapped_column(JSON, default=dict)
    memory: Mapped[dict] = mapped_column(JSON, default=dict)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Execution Details
    last_input: Mapped[Optional[str]] = mapped_column(Text)
    last_output: Mapped[Optional[str]] = mapped_column(Text)
    tool_calls: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<AgentState(id={self.id}, agent={self.agent_name})>"


class AgentTask(Base):
    """Track agent task execution."""
    
    __tablename__ = "agent_tasks"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Task Details
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    orchestrator: Mapped[str] = mapped_column(String(100))
    
    # Input/Output
    input_data: Mapped[dict] = mapped_column(JSON, default=dict)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, running, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Execution Time
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<AgentTask(id={self.id}, type={self.task_type}, status={self.status})>"
