from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class UserInfoParams(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    admin: Optional[bool] = None
    whitelist: Optional[bool] = None
    num: Optional[int] = 100


class UpdateUsersInfoParams(BaseModel):
    user_id: str
    name: Optional[str] = None
    admin: Optional[bool] = None
    whitelist: Optional[bool] = None


class DeleteUserParams(BaseModel):
    user_id: str


class User(BaseModel):
    user_id: str  # fixed can't be changed
    name: str
    admin: bool = False
    whitelist: bool = True
    created_timestamp: int = Field(default_factory=lambda: int(dt.now().timestamp() * 1000))
    updated_timestamp: int = Field(
        default_factory=lambda: int(dt.now().timestamp() * 1000)
    )  # will update automatically when user info is updated

    def update(self, params: UpdateUsersInfoParams):
        if params.name:
            self.name = params.name
        if params.admin is not None:  # can't use if params.admin because it's a bool
            self.admin = params.admin
        if params.whitelist is not None:
            self.whitelist = params.whitelist

        self.updated_timestamp = int(dt.now().timestamp() * 1000)
