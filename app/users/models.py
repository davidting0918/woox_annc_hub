from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime as dt

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
    user_id: str # fixed can't be changed
    name: str
    admin: bool = False
    whitelist: bool = True
    created_timestamp: dt = Field(default_factory=lambda: dt.now())
    updated_timestamp: dt = Field(default_factory=lambda: dt.now()) # will update automatically when user info is updated

    def update(self, params: UpdateUsersInfoParams):
        if params.name:
            self.name = params.name
        if params.admin:
            self.admin = params.admin
        if params.whitelist:
            self.whitelist = params.whitelist
        
        self.updated_timestamp = dt.now()