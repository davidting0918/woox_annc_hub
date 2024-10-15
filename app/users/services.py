# users/services.py
import pandas as pd
from fastapi import HTTPException

from app.config.setting import settings as s
from app.db.dashboard import GCClient
from app.db.database import MongoClient
from app.users.models import (
    DeleteUserParams,
    UpdateUsersInfoParams,
    User,
    UserInfoParams,
)

client = MongoClient(s.dev_db if s.is_test else s.prod_db)
collection = "permission"
gc_client = GCClient()


async def create_user(user: User):
    results = await client.find_one(collection, query={"user_id": user.user_id})
    if results:
        raise HTTPException(status_code=400, detail=f"User already exists with id `{user.user_id}`")
    return await client.insert_one(collection, user.model_dump())


async def list_users_info(params: UserInfoParams):
    query = {k: v for k, v in params.model_dump().items() if v and k not in ["num"]}

    return await client.find_many(collection, query=query, limit=params.num)


async def update_users_info(params: UpdateUsersInfoParams):
    user_data = await client.find_one(collection, query={"user_id": params.user_id})

    if not user_data:
        raise HTTPException(status_code=400, detail=f"User not found with id `{params.user_id}`")

    user = User(**user_data)
    user.update(params)

    return await client.update_one(collection, query={"user_id": params.user_id}, update=user.model_dump())


async def delete_user(params: DeleteUserParams):
    status = await client.delete_one(collection, query={"user_id": params.user_id})
    return {"delete_status": status}


async def in_whitelist(user_id: str):
    user_data = await client.find_one(collection, query={"user_id": user_id})
    return user_data.get("whitelist", False) if user_data else False


async def is_admin(user_id: str):
    user_data = await client.find_one(collection, query={"user_id": user_id})
    return user_data.get("admin", False) if user_data else False


async def update_user_dashboard():
    """
    This function will update the current permission table to the google sheet and only include either admin or whitelist users.
    If both is false, then the user will not be updated to the table
    """
    dashboard = gc_client.get_ws(name="TG User Permission", to_type="ws")
    permissions = pd.DataFrame(
        await client.find_many(collection, query={"$or": [{"admin": True}, {"whitelist": True}]})
    )
    permissions["created_timestamp"] = pd.to_datetime(permissions["created_timestamp"], unit="ms")
    permissions["updated_timestamp"] = pd.to_datetime(permissions["updated_timestamp"], unit="ms")
    permissions["admin"] = permissions["admin"].map({True: "V", False: ""})
    permissions["whitelist"] = permissions["whitelist"].map({True: "V", False: ""})
    permissions = permissions[
        ["user_id", "name", "admin", "whitelist", "created_timestamp", "updated_timestamp"]
    ].sort_values("created_timestamp", ascending=False)

    permissions.columns = [c.replace("_", " ").title() for c in permissions.columns]
    dashboard.clear()
    dashboard.set_dataframe(permissions, start="A1", copy_index=False, copy_head=True)

    return permissions.to_dict(orient="records")
