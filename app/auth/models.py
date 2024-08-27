import uuid
from datetime import datetime as dt

from pydantic import BaseModel, Field


class APIKey(BaseModel):

    created_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))

    @property
    def _id(self):
        return uuid.uuid4().hex
