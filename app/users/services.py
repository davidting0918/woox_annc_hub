# users/services.py
from app.users.models import User, UserInfoParams, UpdateUsersInfoParams, DeleteUserParams
from app.config.setting import settings
from app.db.database import MongoClient
from fastapi import HTTPException, Depends
from datetime import datetime as dt

client = MongoClient(settings.db_name)
collection = 'permission'

async def create_user(user: User):
    results = await client.find_one(
        collection,
        query={
            'user_id': user.user_id
        }
    )
    if results:
        raise HTTPException(status_code=400, detail=f"User already exists with id `{user.user_id}`")
    return await client.insert_one(collection, user.model_dump())

async def list_users_info(params: UserInfoParams):
    query = {
        k: v for k, v in params.model_dump().items() if v and k not in ['num']
    }

    return await client.find_many(collection, query=query, num=params.num)

async def update_users_info(params: UpdateUsersInfoParams):
    user_data = await client.find_one(
        collection,
        query={"user_id": params.user_id}
    )

    if not user_data:
        raise HTTPException(status_code=400, detail=f"User not found with id `{params.user_id}`")

    user = User(**user_data)
    user.update(params)

    return await client.update_one(
        collection,
        query={"user_id": params.user_id},
        update=user.model_dump()
    )

async def delete_user(params: DeleteUserParams):
    status = await client.delete_one(collection, query={"user_id": params.user_id})
    return {
        "delete_status": status
    }