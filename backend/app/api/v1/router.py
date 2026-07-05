"""
API v1 router combining all endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, transactions, investments, dashboard, chat, webhooks, agent_insights, sms, credit_cards, cash_check


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(transactions.router)
api_router.include_router(investments.router)
api_router.include_router(dashboard.router)
api_router.include_router(chat.router)
api_router.include_router(webhooks.router)
api_router.include_router(agent_insights.router)
api_router.include_router(sms.router)
api_router.include_router(credit_cards.router)
api_router.include_router(cash_check.router)
