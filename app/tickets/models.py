# app/tickets/models.py
import asyncio
import time
import uuid
from datetime import datetime as dt
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from telegram import Bot, request
from telegram.error import TelegramError

from app.config.setting import settings as s
from app.users.models import User


class EventBot(Bot):
    REQUEST = request.HTTPXRequest(connection_pool_size=50000, connect_timeout=300, read_timeout=300)

    def __init__(self, **kwargs):
        super().__init__(request=self.REQUEST, **kwargs)


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

    async def approve(self, user: User):
        params = await self.execute()
        params.update(
            {
                "approver_id": user.user_id,
                "approver_name": user.name,
                "status": TicketStatus.approved,
                "status_changed_timestamp": int(dt.now().timestamp() * 1000),
            }
        )

        self.update(**params)

    def reject(self, user: User):
        params = {
            "approver_id": user.user_id,
            "approver_name": user.name,
            "status": TicketStatus.rejected,
            "status_changed_timestamp": int(dt.now().timestamp() * 1000),
        }
        self.update(**params)

    async def execute(self):
        raise NotImplementedError


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

    # values should be {"chat_id": chat_id, "chat_name": chat_name, "message_id": message_id, "status": status}
    success_chats: List[Dict] = Field(default_factory=list)

    # values should be {"chat_id": chat_id, "chat_name": chat_name, "status": status, "error": error}
    failed_chats: List[Dict] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"POST-{self._id}"

    async def execute(self):
        async def send_message(chat):
            try:
                if self.annc_type == AnncType.text:
                    message = await bot.send_message(chat_id=chat["chat_id"], text=self.content_html, parse_mode="HTML")
                elif self.annc_type == AnncType.image:
                    message = await bot.send_photo(
                        chat_id=chat["chat_id"], photo=self.file_path, caption=self.content_html, parse_mode="HTML"
                    )
                elif self.annc_type == AnncType.video:
                    message = await bot.send_video(
                        chat_id=chat["chat_id"], video=self.file_path, caption=self.content_html, parse_mode="HTML"
                    )
                else:
                    message = await bot.send_document(
                        chat_id=chat["chat_id"],
                        document=self.file_path,
                        caption=self.content_html,
                        parse_mode="HTML",
                    )
                return {
                    "chat_id": str(message.chat.id),
                    "chat_name": str(message.chat.title),
                    "message_id": str(message.message_id),
                    "status": True,
                }
            except TelegramError as e:
                return {"chat_id": chat["chat_id"], "chat_name": chat["chat_name"], "status": False, "error": str(e)}

        bot = EventBot(token=s.event_bot_token)

        batch_size = 50
        results = []
        for i in range(0, len(self.chats), batch_size):
            batch = self.chats[i : i + batch_size]
            batch_results = await asyncio.gather(*[send_message(chat) for chat in batch])
            results.extend(batch_results)
            time.sleep(1)

        success_chats = [result for result in results if result["status"]]
        failed_chats = [result for result in results if not result["status"]]
        return {"success_chats": success_chats, "failed_chats": failed_chats}


class EditTicket(Ticket):
    # set inherited fields
    action: TicketAction = TicketAction.edit_annc

    # announcement info related
    old_ticket_id: Optional[str] = None
    old_annc_type: Optional[AnncType] = None
    old_content_text: Optional[str] = None
    old_content_html: Optional[str] = None
    old_content_md: Optional[str] = None

    new_content_text: Optional[str] = None
    new_content_html: Optional[str] = None
    new_content_md: Optional[str] = None

    # chats related
    chats: List[Dict] = Field(default_factory=list)
    success_chats: List[Dict] = Field(default_factory=list)
    failed_chats: List[Dict] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"EDIT-{self._id}"

    async def execute(self):
        async def update_message(chat: Dict):
            try:
                if self.old_annc_type == AnncType.text:
                    message = await bot.edit_message_text(
                        chat_id=chat["chat_id"],
                        message_id=chat["message_id"],
                        text=self.new_content_md,
                        parse_mode="MarkdownV2",
                    )
                else:
                    message = await bot.edit_message_caption(
                        chat_id=chat["chat_id"],
                        message_id=chat["message_id"],
                        caption=self.new_content_md,
                        parse_mode="MarkdownV2",
                    )
                return {
                    "chat_id": str(message.chat.id),
                    "chat_name": str(message.chat.title),
                    "message_id": str(message.message_id),
                    "status": True,
                }
            except TelegramError as e:
                return {
                    "chat_id": chat["chat_id"],
                    "chat_name": chat["chat_name"],
                    "message_id": chat["message_id"],
                    "status": False,
                    "error": str(e),
                }

        bot = EventBot(token=s.event_bot_token)
        batch_size = 50
        results = []
        for i in range(0, len(self.chats), batch_size):
            batch = self.chats[i : i + batch_size]
            batch_results = await asyncio.gather(*[update_message(chat) for chat in batch])
            results.extend(batch_results)
            time.sleep(1)

        success_chats = [result for result in results if result["status"]]
        failed_chats = [result for result in results if not result["status"]]
        return {"success_chats": success_chats, "failed_chats": failed_chats}


class DeleteTicket(Ticket):
    # set inherited fields
    action: TicketAction = TicketAction.delete_annc

    # announcement info related
    old_ticket_id: Optional[str] = None  # should be post ticket id
    old_annc_type: Optional[AnncType] = None
    old_content_text: Optional[str] = None
    old_content_html: Optional[str] = None
    old_content_md: Optional[str] = None
    old_file_path: Optional[str] = None

    # chats related
    chats: List[Dict] = Field(default_factory=list)
    success_chats: List[Dict] = Field(default_factory=list)
    failed_chats: List[Dict] = Field(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_id:
            self.ticket_id = f"DELETE-{self._id}"

    async def execute(self):
        async def delete_message(chat):
            try:
                message = await bot.delete_message(chat_id=chat["chat_id"], message_id=chat["message_id"])
                return {
                    "chat_id": chat["chat_id"],
                    "chat_name": chat["chat_name"],
                    "message_id": chat["message_id"],
                    "status": message,
                }
            except TelegramError as e:
                return {
                    "chat_id": chat["chat_id"],
                    "chat_name": chat["chat_name"],
                    "status": False,
                    "error": str(e),
                }

        bot = EventBot(token=s.event_bot_token)
        batch_size = 50
        results = []
        for i in range(0, len(self.chats), batch_size):
            batch = self.chats[i : i + batch_size]
            batch_results = await asyncio.gather(*[delete_message(chat) for chat in batch])
            results.extend(batch_results)
            time.sleep(1)

        success_chats = [result for result in results if result["status"]]
        failed_chats = [result for result in results if not result["status"]]
        return {"success_chats": success_chats, "failed_chats": failed_chats}


class CreateTicketParams(BaseModel):
    action: TicketAction
    ticket: Dict


class DeleteTicketParams(BaseModel):
    ticket_id: str


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
