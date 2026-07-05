"""
Agent response Pydantic schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class AgentMessage(BaseModel):
    """Schema for agent message."""
    role: str  # user, assistant, system
    content: str
    agent_name: Optional[str] = None
    orchestrator: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: str
    conversation_id: str
    agent_name: str
    orchestrator: str
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: str
    title: Optional[str]
    summary: Optional[str]
    active_orchestrator: Optional[str]
    active_agents: Optional[List[str]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


class ConversationList(BaseModel):
    """Schema for conversation list."""
    items: List[ConversationResponse]
    total: int


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    role: str
    content: str
    agent_name: Optional[str]
    orchestrator: Optional[str]
    tool_calls: Optional[List[Dict[str, Any]]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentTaskResponse(BaseModel):
    """Schema for agent task response."""
    task_id: str
    task_type: str
    agent_name: str
    orchestrator: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SpendingInsight(BaseModel):
    """Schema for spending insight from Money Management Orchestrator."""
    category: str
    current_month: float
    previous_month: float
    change_percentage: float
    insight: str
    recommendations: List[str]


class InvestmentInsight(BaseModel):
    """Schema for investment insight from Investment Orchestrator."""
    portfolio_health: str
    risk_assessment: str
    diversification_score: float
    recommendations: List[str]
    market_outlook: str


class TaxInsight(BaseModel):
    """Schema for tax insight from Financial Products Orchestrator."""
    estimated_tax: float
    potential_savings: float
    regime_comparison: Dict[str, float]
    recommendations: List[str]
    deadline_alerts: List[Dict[str, Any]]


class FinancialReport(BaseModel):
    """Schema for comprehensive financial report."""
    summary: str
    spending_insights: List[SpendingInsight]
    investment_insights: InvestmentInsight
    tax_insights: Optional[TaxInsight] = None
    goals_progress: Optional[List[Dict[str, Any]]] = None
    alerts: Optional[List[str]] = None
    generated_at: datetime


class AgentStreamEvent(BaseModel):
    """Schema for streaming agent events."""
    event_type: str  # thinking, tool_call, response, error
    agent_name: str
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    timestamp: datetime
