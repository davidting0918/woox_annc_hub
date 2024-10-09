from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.services import verify_api_key
from app.chat_info.models import Chat, ChatInfoParams, DeleteChatInfo, UpdateChatInfo
from app.chat_info.services import (
    create_chat,
    delete_chat,
    get_chat_info,
    update_chat_dashboard,
    update_chat_info,
)

router = APIRouter(dependencies=[Depends(verify_api_key)])

# below are get routes


@router.get("/info")
async def get_chat_info_route(
    chat_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    chat_type: Optional[str] = Query(None),
    language: Optional[List[str]] = Query(None),
    category: Optional[List[str]] = Query(None),
    label: Optional[List[str]] = Query(None),
    active: Optional[bool] = True,
    num: Optional[int] = Query(100),
):
    params = ChatInfoParams(
        chat_id=chat_id,
        name=name,
        chat_type=chat_type,
        language=language,
        category=category,
        label=label,
        num=num,
        active=active,
    )
    try:
        res = await get_chat_info(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat info: {str(e)}, params: {params.model_dump()}")


@router.get("/update_dashboard")
async def update_dashboard_route(direction: str):
    try:
        res = await update_chat_dashboard(direction)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat dashboard: {str(e)}")


# below are post routes

# create new chat
@router.post("/create")
async def create_chat_route(chat: Chat):
    try:
        res = await create_chat(chat)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat: {str(e)}, chat: {chat.model_dump()}")


@router.post("/update")
async def update_chat_route(params: UpdateChatInfo):
    try:
        res = await update_chat_info(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat: {str(e)}, chat: {params.model_dump()}")


@router.post("/delete")
async def delete_chat_route(params: DeleteChatInfo):
    try:
        res = await delete_chat(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}, chat: {params.model_dump()}")
