from typing import Optional

from fastapi import APIRouter, HTTPException

from app.tickets.models import (
    CreateTicketParams,
    TicketAction,
    TicketInfoParams,
    TicketStatus,
    UpdateTicketParams,
)
from app.tickets.services import create_ticket, get_ticket_info, update_post_ticket

router = APIRouter()


# below is `get` endpoints

# get ticket info
@router.get("/info/")
async def get_ticket_info_route(
    ticket_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    start_created_timestamp: Optional[str] = None,
    end_created_timestamp: Optional[str] = None,
    start_status_changed_timestamp: Optional[str] = None,
    end_status_changed_timestamp: Optional[str] = None,
    status: Optional[TicketStatus] = None,
    num: Optional[int] = 100,
):
    params = TicketInfoParams(
        ticket_id=ticket_id,
        creator_id=creator_id,
        start_created_timestamp=start_created_timestamp,
        end_created_timestamp=end_created_timestamp,
        start_status_changed_timestamp=start_status_changed_timestamp,
        end_status_changed_timestamp=end_status_changed_timestamp,
        status=status,
        num=num,
    )
    try:
        res = await get_ticket_info(params)
        return {
            "status": 1,
            "data_num": len(res),
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticket info: {e}")


# below is `post` endpoints
@router.post("/create/")
async def create_ticket_route(params: CreateTicketParams):
    try:
        res = await create_ticket(params)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {e}")


@router.post("/update/")
async def update_ticket_router(params: UpdateTicketParams):
    method_map = {
        TicketAction.post_annc: update_post_ticket,
        TicketAction.edit_annc: None,
        TicketAction.delete_annc: None,
        TicketAction.update_user: None,
    }
    try:
        res = await method_map[params.ticket_action](params)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ticket: {e}")
