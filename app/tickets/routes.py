from fastapi import APIRouter
from app.tickets.models import TicketStatus, Announcement, PostTicket, EditTicket, DeleteTicket, CreateTicketParams, TicketInfoParams
from typing import Optional
from app.tickets.services import get_ticket_info, create_ticket
from fastapi import HTTPException

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
    num: Optional[int] = 100
):
    params = TicketInfoParams(
        ticket_id=ticket_id,
        creator_id=creator_id,
        start_created_timestamp=start_created_timestamp,
        end_created_timestamp=end_created_timestamp,
        start_status_changed_timestamp=start_status_changed_timestamp,
        end_status_changed_timestamp=end_status_changed_timestamp,
        status=status,
        num=num
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
async def create_ticket_route(
    params: CreateTicketParams
):
    try:
        res = await create_ticket(params)
        return {
            "status": 1,
            "data": res,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {e}")


