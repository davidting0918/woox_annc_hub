from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime as dt

class User(BaseModel):
    user_id: str 
    name: str
    admin: bool = False
    whitelist: bool = True
    created_timestamp: dt = Field(default_factory=lambda: dt.now())
    updated_timestamp: dt = Field(default_factory=lambda: dt.now())

    def change_permission(self, admin: Optional[bool], whitelist: Optional[bool]):
        if admin:
            self.admin = admin
        if whitelist:
            self.whitelist = whitelist
        
        self.updated_timestamp = dt.now()

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