"""\
Notification Pydantic schemas
"""

from datetime import datetime
from typing import Any, Dict, Optional, List

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    payload: Dict[str, Any]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    items: List[NotificationResponse]
    total: int


class NotificationMarkReadResponse(BaseModel):
    success: bool
