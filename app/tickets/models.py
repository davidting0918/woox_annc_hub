from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime as dt
from enum import Enum
from app.chat_info.models import Chat
from app.users.models import User
import uuid

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

# Shared models

class TimestampModdel(BaseModel):
    created_timestamp: str = Field(default_factory=dt.now().isoformat())
    updated_timestamp: str = Field(default_factory=dt.now().isoformat())

    @property
    def _id(self):
        return uuid.uuid4().hex[:]
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_timestamp = dt.now().isoformat()


class Announcement(TimestampModdel):
    annc_id: str  # fixed when created

    # define content related fields
    annc_type: Optional[AnncType] = None
    content_text: Optional[str] = None
    content_html: Optional[str] = None
    content_md: Optional[str] = None
    file_id: Optional[str] = None

    # define chats related fields
    category: Optional[str] = None
    language: Optional[str] = None
    label: Optional[List[str]] = None
    chats: List[Chat] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.annc_id = f"ANN-{self._id}"


    def post(self):
        pass

class Ticket(TimestampModdel):
    ticket_id: str
    action: TicketAction
    status: TicketStatus

    # user related fields
    creator_id: str  # fixed when created, using user_id from telegram
    creator_name: str  # fixed when created, using name from telegram
    approver_id: Optional[str] = None
    approver_name: Optional[str] = None

    status_changed_timestamp: Optional[str] = None

    def approve(self, user: User):
        params = {
            "approver_id": user.user_id,
            "approver_name": user.name,
            "status": TicketStatus.approved,
            "status_changed_timestamp": dt.now().isoformat()
        }
        self.update(**params)

    def reject(self, user: User):
        params = {
            "approver_id": user.user_id,
            "approver_name": user.name,
            "status": TicketStatus.rejected,
            "status_changed_timestamp": dt.now().isoformat()
        }
        self.update(**params)

class PostTicket(Ticket):
    annc: Announcement
    actual_chats: List[Chat] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticket_id = f"POST-{self._id}"
        self.action = TicketAction.post_annc
        self.status = TicketStatus.pending


class EditTicket(Ticket):
    old_annc: Announcement
    new_annc: Announcement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticket_id = f"EDIT-{self._id}"
        self.action = TicketAction.edit_annc
        self.status = TicketStatus.pending

class EditTicket(Ticket):
    annc: Announcement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ticket_id = f"EDIT-{self._id}"
        self.action = TicketAction.edit_annc
        self.status = TicketStatus.pending