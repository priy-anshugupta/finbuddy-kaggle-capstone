"""
Schemas module exports
"""

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserProfile,
    TokenResponse,
    TokenRefresh,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm
)
from app.schemas.transaction import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionFilter,
    TransactionStats,
    RecurringTransactionResponse,
    BulkTransactionUpload,
    OCRUploadResponse
)
from app.schemas.investment import (
    InvestmentBase,
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
    InvestmentList,
    InvestmentHoldingCreate,
    InvestmentHoldingResponse,
    PortfolioSummary,
    PortfolioAllocation,
    InvestmentRecommendation,
    WatchlistCreate,
    WatchlistResponse
)
from app.schemas.agent_response import (
    AgentMessage,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationList,
    MessageResponse,
    AgentTaskResponse,
    SpendingInsight,
    InvestmentInsight,
    TaxInsight,
    FinancialReport,
    AgentStreamEvent
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "TokenResponse",
    "TokenRefresh",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    # Transaction
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "TransactionResponse",
    "TransactionList",
    "TransactionFilter",
    "TransactionStats",
    "RecurringTransactionResponse",
    "BulkTransactionUpload",
    "OCRUploadResponse",
    # Investment
    "InvestmentBase",
    "InvestmentCreate",
    "InvestmentUpdate",
    "InvestmentResponse",
    "InvestmentList",
    "InvestmentHoldingCreate",
    "InvestmentHoldingResponse",
    "PortfolioSummary",
    "PortfolioAllocation",
    "InvestmentRecommendation",
    "WatchlistCreate",
    "WatchlistResponse",
    # Agent
    "AgentMessage",
    "ChatRequest",
    "ChatResponse",
    "ConversationCreate",
    "ConversationResponse",
    "ConversationList",
    "MessageResponse",
    "AgentTaskResponse",
    "SpendingInsight",
    "InvestmentInsight",
    "TaxInsight",
    "FinancialReport",
    "AgentStreamEvent",
]
