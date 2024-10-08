from datetime import datetime as dt
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChatType(str, Enum):
    group = "group"
    channel = "channel"
    supergroup = "supergroup"


class ChatInfoParams(BaseModel):
    chat_id: Optional[str] = None
    name: Optional[str] = None
    chat_type: Optional[ChatType] = None
    language: Optional[list[str]] = None
    category: Optional[list[str]] = None
    label: Optional[list[str]] = None
    num: Optional[int] = 100


class UpdateChatInfo(BaseModel):
    chat_id: str  # required
    name: Optional[str] = None
    chat_type: Optional[ChatType] = None
    language: Optional[list[str]] = None
    category: Optional[list[str]] = None
    label: Optional[list[str]] = None
    active: Optional[bool] = None
    description: Optional[str] = None


class DeleteChatInfo(BaseModel):
    chat_id: str  # required


class Chat(BaseModel):
    chat_id: str  # fixed can't be changed
    name: str
    chat_type: ChatType
    language: list[str] = []
    category: list[str] = []
    label: list[str] = []
    active: bool = True  # default is true
    created_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))
    updated_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))
    description: Optional[str] = None

    def update(self, params: UpdateChatInfo):
        if params.name:
            self.name = params.name
        if params.chat_type:
            self.chat_type = params.chat_type
        if params.language is not None:
            self.language = params.language
        if params.category is not None:
            self.category = params.category
        if params.label is not None:
            self.label = params.label
        if params.active is not None:
            self.active = params.active
        if params.description is not None:
            self.description = params.description

        self.updated_timestamp = int(dt.now().timestamp() * 1000)
