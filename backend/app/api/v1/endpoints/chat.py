"""
Chat API endpoints for agent interactions
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio

from app.dependencies import get_db, CurrentUser
from app.models.conversation import Conversation, Message, MessageRole
from app.schemas.agent_response import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationList,
    MessageResponse
)


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/conversations", response_model=ConversationList)
async def get_conversations(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """Get user's conversations."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    conversations = result.scalars().all()
    
    # Add message count
    conversation_list = []
    for conv in conversations:
        result = await db.execute(
            select(Message).where(Message.conversation_id == conv.id)
        )
        messages = result.scalars().all()
        
        conv_dict = {
            "id": conv.id,
            "title": conv.title,
            "summary": conv.summary,
            "active_orchestrator": conv.active_orchestrator,
            "active_agents": conv.active_agents,
            "is_active": conv.is_active,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": len(messages)
        }
        conversation_list.append(ConversationResponse(**conv_dict))
    
    return ConversationList(
        items=conversation_list,
        total=len(conversation_list)
    )


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title or "New Conversation",
        context=conversation_data.context or {}
    )
    
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        summary=conversation.summary,
        active_orchestrator=conversation.active_orchestrator,
        active_agents=conversation.active_agents,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == current_user.id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get message count
    result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    messages = result.scalars().all()
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        summary=conversation.summary,
        active_orchestrator=conversation.active_orchestrator,
        active_agents=conversation.active_agents,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=len(messages)
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    """Get messages for a conversation."""
    # Verify conversation belongs to user
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=m.id,
            role=m.role.value,
            content=m.content,
            agent_name=m.agent_name,
            orchestrator=m.orchestrator,
            tool_calls=m.tool_calls,
            created_at=m.created_at
        )
        for m in messages
    ]


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get agent response."""
    # Get or create conversation
    if chat_request.conversation_id:
        result = await db.execute(
            select(Conversation)
            .where(Conversation.id == chat_request.conversation_id)
            .where(Conversation.user_id == current_user.id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title="New Conversation"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content=chat_request.message
    )
    db.add(user_message)
    
    # TODO: Process message through agent orchestrators
    # This is where we'll integrate with the agent system
    
    # For now, return a placeholder response
    agent_response = await process_with_agents(
        message=chat_request.message,
        user=current_user,
        conversation=conversation,
        context=chat_request.context,
        db=db
    )
    
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role=MessageRole.ASSISTANT,
        content=agent_response["message"],
        agent_name=agent_response["agent_name"],
        orchestrator=agent_response["orchestrator"]
    )
    db.add(assistant_message)
    
    # Update conversation
    conversation.updated_at = datetime.utcnow()
    conversation.active_orchestrator = agent_response["orchestrator"]
    
    await db.commit()
    
    return ChatResponse(
        message=agent_response["message"],
        conversation_id=conversation.id,
        agent_name=agent_response["agent_name"],
        orchestrator=agent_response["orchestrator"],
        suggestions=agent_response.get("suggestions"),
        actions=agent_response.get("actions")
    )


@router.post("/send/stream")
async def send_message_stream(
    chat_request: ChatRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Send a message and stream the agent response."""
    
    async def generate():
        # TODO: Implement streaming with agents
        # This will stream agent thinking, tool calls, and responses
        
        events = [
            {"event": "thinking", "agent": "router", "content": "Analyzing your request..."},
            {"event": "thinking", "agent": "money_growth", "content": "Looking at your spending patterns..."},
            {"event": "response", "agent": "money_growth", "content": "Based on your transaction history, I can see..."}
        ]
        
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.5)
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == current_user.id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()


async def process_with_agents(
    message: str,
    user,
    conversation,
    context: Optional[dict],
    db: AsyncSession
) -> dict:
    """
    Process user message through the agent system.
    
    Uses Google Gemini for AI responses with real user financial data.
    """
    from app.core.logging import get_logger
    from app.config import settings
    from app.models.transaction import Transaction, TransactionType
    from app.models.investment import Investment
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    logger = get_logger(__name__)
    message_lower = message.lower()
    
    # ── Fetch real user data for context ──────────────────────────────
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get this month's transactions
    tx_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .where(Transaction.transaction_date >= month_start)
        .order_by(Transaction.transaction_date.desc())
    )
    transactions = tx_result.scalars().all()
    
    # Calculate summaries
    total_income = sum(t.amount for t in transactions if t.transaction_type == TransactionType.CREDIT)
    total_expense = sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEBIT)
    savings = total_income - total_expense
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    # Category breakdown
    category_spending = {}
    for t in transactions:
        if t.transaction_type == TransactionType.DEBIT:
            cat = t.category.value if t.category else "other"
            category_spending[cat] = category_spending.get(cat, 0) + t.amount
    
    # Get investments
    inv_result = await db.execute(
        select(Investment).where(Investment.user_id == user.id)
    )
    investments = inv_result.scalars().all()
    
    total_invested = sum(i.invested_amount for i in investments if i.invested_amount)
    total_current = sum(i.current_value for i in investments if i.current_value)
    portfolio_return = ((total_current - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    # Recent transactions text
    recent_tx = []
    for t in transactions[:10]:
        tx_type = "+" if t.transaction_type == TransactionType.CREDIT else "-"
        recent_tx.append(f"  {tx_type}₹{t.amount:,.0f} | {t.category.value if t.category else 'other'} | {t.description or t.merchant_name or 'N/A'}")
    
    # Investment summary text
    inv_summary = []
    for i in investments:
        ret = f"+{i.percentage_return:.1f}%" if i.percentage_return and i.percentage_return >= 0 else f"{i.percentage_return:.1f}%"
        inv_summary.append(f"  {i.name}: ₹{i.current_value:,.0f} ({ret})")
    
    # ── Build context-rich prompt ─────────────────────────────────────
    financial_context = f"""
USER FINANCIAL DATA (This Month - {now.strftime('%B %Y')}):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Monthly Income: ₹{total_income:,.0f}
Total Expenses: ₹{total_expense:,.0f}
Net Savings: ₹{savings:,.0f}
Savings Rate: {savings_rate:.1f}%

SPENDING BY CATEGORY:
{chr(10).join(f'  {cat}: ₹{amt:,.0f}' for cat, amt in sorted(category_spending.items(), key=lambda x: -x[1]))}

RECENT TRANSACTIONS:
{chr(10).join(recent_tx) if recent_tx else '  No transactions this month'}

INVESTMENT PORTFOLIO (Total: ₹{total_current:,.0f} | Return: {portfolio_return:+.1f}%):
{chr(10).join(inv_summary) if inv_summary else '  No investments'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    system_prompt = f"""You are FinBuddy, an AI-powered personal financial assistant for Indian users.
You have access to the user's REAL financial data shown below. Use this data to give personalized, specific advice.

{financial_context}

RULES:
1. Always reference the user's ACTUAL numbers — don't make up data
2. Use Indian Rupees (₹) for all amounts
3. Apply the 50/30/20 budgeting rule (50% needs, 30% wants, 20% savings)
4. Be specific — mention exact amounts and percentages
5. Format responses with clear sections, bullet points, and emoji
6. Keep responses concise but actionable (under 300 words)
7. For investment advice, add disclaimer: "This is educational, not financial advice"
"""

    # ── Determine agent routing ───────────────────────────────────────
    if any(w in message_lower for w in ["invest", "stock", "mutual fund", "sip", "portfolio", "market", "nifty"]):
        agent_name = "investment_agent"
        orchestrator_name = "orchestrator_2"
        suggestions = ["View my portfolio", "SIP recommendations", "Analyze market trends"]
    elif any(w in message_lower for w in ["tax", "itr", "credit card", "loan", "emi", "insurance"]):
        agent_name = "financial_products_agent"
        orchestrator_name = "orchestrator_3"
        suggestions = ["Calculate income tax", "Compare credit cards", "Check loan eligibility"]
    elif any(w in message_lower for w in ["spend", "expense", "budget", "saving", "category", "money"]):
        agent_name = "money_growth_agent"
        orchestrator_name = "orchestrator_1"
        suggestions = ["Show spending by category", "50/30/20 analysis", "Set a budget"]
    else:
        agent_name = "finbuddy"
        orchestrator_name = "orchestrator_1"
        suggestions = ["Show my spending summary", "Analyze my investments", "Help me save more"]

    # ── Call Google Gemini ────────────────────────────────────────────
    try:
        from google import genai
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        gemini_response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": system_prompt + "\n\nUser Question: " + message}]}
            ],
        )
        
        response = gemini_response.text
        logger.info(f"Gemini response generated", agent=agent_name, orchestrator=orchestrator_name)
        
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        # Fallback: generate a data-driven response without LLM
        response = f"""📊 **Your Financial Summary — {now.strftime('%B %Y')}**

💰 **Income**: ₹{total_income:,.0f}
💸 **Expenses**: ₹{total_expense:,.0f}
🏦 **Savings**: ₹{savings:,.0f} ({savings_rate:.1f}%)

📈 **Portfolio Value**: ₹{total_current:,.0f} (Return: {portfolio_return:+.1f}%)

**Top Spending Categories:**
{chr(10).join(f'• {cat.title()}: ₹{amt:,.0f}' for cat, amt in sorted(category_spending.items(), key=lambda x: -x[1])[:5])}

💡 Try asking me specific questions like "Am I saving enough?" or "Should I increase my SIP?"
"""

    return {
        "message": response,
        "agent_name": agent_name,
        "orchestrator": orchestrator_name,
        "suggestions": suggestions,
        "actions": []
    }

