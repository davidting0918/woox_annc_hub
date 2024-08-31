import uuid
from datetime import datetime as dt
from enum import Enum
from typing import List, Optional

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


# Shared models


class TimestampModel(BaseModel):
    created_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))
    updated_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))

    @property
    def _id(self):
        return uuid.uuid4().hex

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                if key == "annc":
                    setattr(self, key, Announcement(**value))
                    continue

                setattr(self, key, value)
        self.updated_timestamp = int(dt.now().timestamp() * 1000)


class Announcement(BaseModel):

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
    chats: List[str] = Field(default_factory=list)  # values should be chat_id
    actual_chats: List[str] = Field(default_factory=list)  # values should be chat_id

    @property
    def annc_id(self):
        return f"ANN-{uuid.uuid4().hex}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def post(self):
        pass


class Ticket(TimestampModel):
    ticket_id: Optional[str] = None
    action: TicketAction
    status: TicketStatus

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
    annc: Announcement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"POST-{self._id}"
        if not self.status:
            self.status = TicketStatus.pending
        self.action = TicketAction.post_annc


class EditTicket(Ticket):
    old_annc: Announcement
    new_annc: Announcement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"EDIT-{self._id}"
        if not self.status:
            self.status = TicketStatus.pending
        self.action = TicketAction.edit_annc


class DeleteTicket(Ticket):
    annc: Announcement

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"DELETE-{self._id}"
        if not self.status:
            self.status = TicketStatus.pending
        self.action = TicketAction.delete_annc


class CreateTicketParams(BaseModel):
    ticket: PostTicket | EditTicket | DeleteTicket


class DeleteTicketParams(BaseModel):
    ticket_id: str


class UpdateTicketParams(BaseModel):
    ticket_id: str
    ticket_action: TicketAction
    ticket: PostTicket | EditTicket | DeleteTicket


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
