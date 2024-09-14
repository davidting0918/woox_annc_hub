# app/tickets/models.py
import uuid
from datetime import datetime as dt
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.users.models import User


# Enum definitions
class TicketAction(str, Enum):
    post_annc = "post_annc"
    edit_annc = "edit_annc"
    delete_annc = "delete_annc"
    update_user = "update_user"


class AnncType(str, Enum):
    text = "text"
    image = "image"
    video = "video"
    file = "file"


class TicketStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class TimestampModel(BaseModel):
    created_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))
    updated_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))

    @property
    def _id(self):
        return uuid.uuid4().hex

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_timestamp = int(dt.now().timestamp() * 1000)


class Ticket(TimestampModel):
    ticket_id: Optional[str] = None
    action: TicketAction
    status: TicketStatus = TicketStatus.pending

    # user related fields
    creator_id: str  # fixed when created, using user_id from telegram
    creator_name: str  # fixed when created, using name from telegram
    approver_id: Optional[str] = None
    approver_name: Optional[str] = None

    status_changed_timestamp: Optional[int] = None

    def approve(self, user: User):
        params = {
            "approver_id": user.user_id,
            "approver_name": user.name,
            "status": TicketStatus.approved,
            "status_changed_timestamp": int(dt.now().timestamp() * 1000),
        }
        self.update(**params)

    def reject(self, user: User):
        params = {
            "approver_id": user.user_id,
            "approver_name": user.name,
            "status": TicketStatus.rejected,
            "status_changed_timestamp": int(dt.now().timestamp() * 1000),
        }
        self.update(**params)


class PostTicket(Ticket):
    # set inherited fields
    action: TicketAction = TicketAction.post_annc

    # announcement related field
    annc_type: Optional[AnncType] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    content_md: Optional[str] = None
    file_path: Optional[str] = None

    # define chats related fields
    category: Optional[str] = None
    language: Optional[str] = None
    label: Optional[List[str]] = None

    # values should be {"chat_id": chat_id, "chat_name": chat_name}
    chats: List[Dict] = Field(default_factory=list)

    # values should be {"chat_id": chat_id, "chat_name": chat_name, "message_id": message_id}
    actual_chats: List[Dict] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"POST-{self._id}"


class EditTicket(Ticket):
    # set inherited fields
    action: TicketAction = TicketAction.edit_annc

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"EDIT-{self._id}"


class DeleteTicket(Ticket):
    # set inherited fields
    action: TicketAction = TicketAction.delete_annc

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"DELETE-{self._id}"


class CreateTicketParams(BaseModel):
    action: TicketAction
    ticket: Dict


class TicketInfoParams(BaseModel):
    ticket_id: Optional[str] = None
    creator_id: Optional[str] = None
    start_created_timestamp: Optional[int] = None
    end_created_timestamp: Optional[int] = None
    start_status_changed_timestamp: Optional[int] = None
    end_status_changed_timestamp: Optional[int] = None
    status: Optional[TicketStatus] = None
    action: Optional[TicketAction] = None
    num: Optional[int] = None


class ApproveRejectTicketParams(BaseModel):
    ticket_id: str
    user_id: str
