from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime as dt
from enum import Enum

class TicketAction(str, Enum):
    post_annc = "post_annc"
    update_annc = "update_annc"
    delete_annc = "delete_annc"

    add_user = "add_user"
    update_user = "update_user"
    delete_user = "delete_user"

class TicketStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class Ticket(BaseModel):
    """
    This is the base model for all tickets, all tickets should inherit from this model
    """
    ticket_id: str  # fixed when created
    creator_id: str  # fixed when created
    creator_name: str  # fixed when created
    action: TicketAction
    approver_id: Optional[str] = None
    approver_name: Optional[str] = None
    created_timestamp: dt = Field(default_factory=dt.now)
    updated_timestamp: dt = Field(default_factory=dt.now)
    approved_timestamp: Optional[dt] = None
    status: TicketStatus = TicketStatus.pending

class NewAnncTicket(Ticket):
    action: TicketAction = TicketAction.post_annc