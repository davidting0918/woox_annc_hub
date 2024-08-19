from app.config.setting import settings
from app.chat_info.services import create_chat, get_chat_info
from fastapi import APIRouter, Body, HTTPException
from app.chat_info.models import Chat, UpdateChatInfo, ChatInfoParams

router = APIRouter()

# below are get routes

@router.get("/info")
async def get_chat_info_route(params: ChatInfoParams):
    try:
        res = await get_chat_info(params)
        return {
            "status": 1,
            "data": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat info: {str(e)}, params: {params.model_dump()}")

# below are post routes

# create new chat
@router.post("/create")
async def create_chat_route(chat: Chat):
    try:
        res = await create_chat(chat)
        return {
            "status": 1,
            "data": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat: {str(e)}, chat: {chat.model_dump()}")


