from app.chat_info.models import Chat, UpdateChatInfo, ChatInfoParams, DeleteChatInfo
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
    2. `chat_type`, `language`, `category`, `label` can combine with `num`
        and logic will be `OR` between params and `AND` within each param
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

async def update_chat_info(params: UpdateChatInfo):
    chat_data = await client.find_one(
        collection,
        query={
            "chat_id": params.chat_id
        }
    )
    if not chat_data:
        raise HTTPException(status_code=400, detail=f"Chat not found with id `{params.chat_id}`")
    

    chat = Chat(**chat_data)
    chat.update(params.model_dump())
    return await client.update_one(
        collection,
        query={
            "chat_id": params.chat_id
        },
        data=chat.model_dump()
    )

async def delete_chat(params: DeleteChatInfo):
    status = await client.delete_one(
        collection,
        query={
            "chat_id": params.chat_id
        }
    )

    return {
        "delete_status": status
    }