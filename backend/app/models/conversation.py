"""
Conversation and message models for chat functionality
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Conversation(Base):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversations"
    
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
    
    # Conversation Details
    title: Mapped[Optional[str]] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Context
    active_orchestrator: Mapped[Optional[str]] = mapped_column(String(100))
    active_agents: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    context: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    """Message model for individual chat messages."""
    
    __tablename__ = "messages"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True
    )
    
    # Message Content
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Agent Information
    agent_name: Mapped[Optional[str]] = mapped_column(String(100))
    orchestrator: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Tool Calls
    tool_calls: Mapped[Optional[list]] = mapped_column(JSON)
    tool_call_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Metadata
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Tokens
    prompt_tokens: Mapped[Optional[int]] = mapped_column()
    completion_tokens: Mapped[Optional[int]] = mapped_column()
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"
