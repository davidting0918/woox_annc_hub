from fastapi import HTTPException

from app.chat_info.models import Chat, ChatInfoParams, DeleteChatInfo, UpdateChatInfo
from app.config.setting import settings as s
from app.db.database import MongoClient

client = MongoClient(s.dev_db if s.is_test else s.prod_db)
collection = "chat_info"


async def create_chat(chat: Chat):
    res = await client.find_one(collection, query={"chat_id": chat.chat_id})
    if res:
        raise HTTPException(status_code=400, detail=f"Chat already exists with id `{chat.chat_id}`")

    return await client.insert_one(collection, chat.model_dump())


async def get_chat_info(params: ChatInfoParams):
    """
    Query params have the following case:
    1. `chat_id`, `name` won't combine with other params
    2. `chat_type`, `language`, `category`, `label` can combine with `num`
        and logic will be `OR` between params and `AND` within each param
    """
    if params.chat_id:
        return [await client.find_one(collection, query={"chat_id": params.chat_id})]

    if params.name:
        return [await client.find_one(collection, query={"name": params.name})]

    query = {}
    if params.chat_type:
        query["chat_type"] = params.chat_type
    if params.language:
        query["language"] = {"$in": params.language}
    if params.category:
        query["category"] = {"$in": params.category}
    if params.label:
        query["label"] = {"$in": params.label}

    return await client.find_many(collection, query=query, limit=params.num)


async def update_chat_info(params: UpdateChatInfo):
    chat_data = await client.find_one(collection, query={"chat_id": params.chat_id})
    if not chat_data:
        raise HTTPException(status_code=400, detail=f"Chat not found with id `{params.chat_id}`")

    chat = Chat(**chat_data)
    chat.update(params)
    return await client.update_one(collection, query={"chat_id": params.chat_id}, update=chat.model_dump())


async def delete_chat(params: DeleteChatInfo):
    status = await client.delete_one(collection, query={"chat_id": params.chat_id})

    return {"delete_status": status}


async def update_chat_dashboard(direction: str = "pull"):
    """
    This function will pull or push chat info to the google sheet,
    1. push is using when chat name, chat type, new chat created, deleted chat status changed
    2. pull is using whenever a user request to create a ticket, udpate the category, language, label on the dashboard to mongodb
    """
    return
