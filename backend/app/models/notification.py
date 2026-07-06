from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class NotificationType(str, Enum):
    sms = "sms"
    email = "email"
    push = "push"

class NotificationStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    mock = "mock"

class NotificationProvider(str, Enum):
    twilio = "twilio"
    sendgrid = "sendgrid"
    mock = "mock"

class Notification(BaseModel):
    id: str
    type: NotificationType
    recipients: List[str]
    subject: Optional[str] = None
    message: str
    status: NotificationStatus
    provider: NotificationProvider
    incident_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
