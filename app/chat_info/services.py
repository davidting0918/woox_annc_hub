from app.chat_info.models import Chat, UpdateChatInfoParams, ChatInfoParams
from app.config.setting import settings
from app.db.database import MongoClient
from fastapi import HTTPException

client = MongoClient(settings.db_name)
collection = "chat_info"


async def create_chat(chat: Chat):
    res = await client.find_one(
        collection,
        query={
            "chat_id": chat.chat_id
        }
    )
    if res:
        raise HTTPException(status_code=400, detail=f"Chat already exists with id `{chat.chat_id}`")
    
    res = await client.insert_one(
        collection,
        chat.model_dump()
    )
    return res

async def get_chat_info(params: ChatInfoParams):
    """
    Query params have the following case:
    1. `chat_id`, `name` won't combine with other params
    """
    if params.chat_id:
        return await client.find_one(
            collection, 
            query={
                "chat_id": params.chat_id
            }
        )
    
    if params.name:
        return await client.find_one(
            collection, 
            query={
                "name": params.name
            }
        )
    
    query = {
        k: {
            "$in": v
        } for k, v in params.model_dump().items() if v and k in ['chat_type', 'language', 'category', 'label']
    }
    return await client.find_many(
        collection,
        query=query,
        limit=params.num
    )