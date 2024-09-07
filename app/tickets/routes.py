from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.auth.services import verify_api_key
from app.tickets.models import (
    CreateTicketParams,
    DeleteTicketParams,
    TicketAction,
    TicketInfoParams,
    TicketStatus,
    UpdateTicketParams,
)
from app.tickets.services import (
    approve_ticket,
    create_ticket,
    delete_ticket,
    get_ticket_info,
    reject_ticket,
    update_post_ticket,
)

router = APIRouter(dependencies=[Depends(verify_api_key)])


# below is `get` endpoints

# get ticket info
@router.get("/info")
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
@router.post("/create")
async def create_ticket_route(params: CreateTicketParams):
    try:
        res = await create_ticket(params)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {e}")


@router.post("/approve")
async def approve_ticket_route(ticket_id: str, user_id: str):
    try:
        res = await approve_ticket(ticket_id, user_id)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving ticket: {e}")


@router.post("/reject")
async def reject_ticket_route(ticket_id: str, user_id: str):
    try:
        res = await reject_ticket(ticket_id, user_id)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting ticket: {e}")


@router.post("/update")
async def update_ticket_route(params: UpdateTicketParams):
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


@router.post("/delete")
async def delete_ticket_route(params: DeleteTicketParams):
    try:
        res = await delete_ticket(params)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting ticket: {e}")
