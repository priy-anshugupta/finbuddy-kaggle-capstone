"""
Webhook endpoints for external integrations
"""

from fastapi import APIRouter, HTTPException, status, Header, Request
from typing import Optional
import hmac
import hashlib

from app.config import settings


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/plaid")
async def plaid_webhook(
    request: Request,
    plaid_verification: Optional[str] = Header(None, alias="Plaid-Verification")
):
    """
    Handle Plaid webhooks for bank account updates.
    
    Webhook types:
    - TRANSACTIONS: New transactions available
    - ITEM: Item status changes
    - AUTH: Auth data available
    """
    body = await request.json()
    
    webhook_type = body.get("webhook_type")
    webhook_code = body.get("webhook_code")
    
    if webhook_type == "TRANSACTIONS":
        if webhook_code == "SYNC_UPDATES_AVAILABLE":
            # New transactions available
            item_id = body.get("item_id")
            # TODO: Trigger transaction sync for the item
            return {"status": "processing", "action": "sync_transactions"}
        
        elif webhook_code == "INITIAL_UPDATE":
            # Initial historical transactions ready
            item_id = body.get("item_id")
            return {"status": "processing", "action": "initial_sync"}
    
    elif webhook_type == "ITEM":
        if webhook_code == "ERROR":
            # Item has an error
            item_id = body.get("item_id")
            error = body.get("error")
            # TODO: Notify user about the error
            return {"status": "error_logged", "item_id": item_id}
        
        elif webhook_code == "PENDING_EXPIRATION":
            # Access token expiring
            item_id = body.get("item_id")
            # TODO: Notify user to re-authenticate
            return {"status": "expiration_logged", "item_id": item_id}
    
    return {"status": "received", "webhook_type": webhook_type, "webhook_code": webhook_code}


@router.post("/sms")
async def sms_webhook(request: Request):
    """
    Handle incoming SMS for transaction parsing.
    
    This can be connected to services like Twilio or custom SMS gateways.
    """
    body = await request.json()
    
    sender = body.get("from")
    message = body.get("message")
    timestamp = body.get("timestamp")
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content required"
        )
    
    # TODO: Route to OCR Agent for transaction extraction
    # This would trigger the OCR Agent to:
    # 1. Parse the SMS message
    # 2. Extract transaction details
    # 3. Create a transaction record
    
    return {
        "status": "received",
        "action": "processing",
        "message_preview": message[:50] + "..." if len(message) > 50 else message
    }


@router.post("/market-update")
async def market_update_webhook(
    request: Request,
    x_api_key: Optional[str] = Header(None)
):
    """
    Handle market data updates from external providers.
    """
    # Verify API key
    if x_api_key != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    body = await request.json()
    
    update_type = body.get("type")  # price_update, news, alert
    symbols = body.get("symbols", [])
    data = body.get("data")
    
    if update_type == "price_update":
        # TODO: Update investment current prices
        # TODO: Check for price alerts
        return {"status": "processing", "symbols_count": len(symbols)}
    
    elif update_type == "news":
        # TODO: Route to News Agent for processing
        return {"status": "processing", "action": "news_analysis"}
    
    elif update_type == "alert":
        # TODO: Send user notification
        return {"status": "processing", "action": "user_notification"}
    
    return {"status": "received", "update_type": update_type}


@router.post("/payment-reminder")
async def payment_reminder_webhook(request: Request):
    """
    Handle payment reminder callbacks from scheduled tasks.
    """
    body = await request.json()
    
    user_id = body.get("user_id")
    payment_type = body.get("payment_type")
    payment_name = body.get("payment_name")
    amount = body.get("amount")
    due_date = body.get("due_date")
    
    # TODO: Send notification to user
    # TODO: Add to upcoming payments list
    
    return {
        "status": "reminder_scheduled",
        "user_id": user_id,
        "payment": payment_name
    }


def verify_webhook_signature(
    payload: bytes,
    signature: str,
    secret: str
) -> bool:
    """Verify webhook signature for security."""
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
