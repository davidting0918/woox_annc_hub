from app.config.setting import settings
from app.chat_info.services import create_chat, get_chat_info, update_chat_info, delete_chat
from fastapi import APIRouter, Body, HTTPException
from app.chat_info.models import Chat, UpdateChatInfo, ChatInfoParams, DeleteChatInfo

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

@router.post("/update")
async def update_chat_route(params: UpdateChatInfo):
    try:
        res = await update_chat_info(params)
        return {
            "status": 1,
            "data": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat: {str(e)}, chat: {params.model_dump()}")
    

@router.post("/delete")
async def delete_chat_route(params: DeleteChatInfo):
    try:
        res = await delete_chat(params)
        return {
            "status": 1,
            "data": res
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}, chat: {params.model_dump()}")