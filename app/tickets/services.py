from app.tickets.models import Announcement, PostTicket, EditTicket, DeleteTicket, CreateTicketParams, TicketInfoParams
from app.db.database import MongoClient
from app.config.setting import settings
from fastapi import HTTPException

client = MongoClient(settings.db_name)
collection = 'ticket_records'


# Below is get endpoints related functions
async def get_ticket_info(params: TicketInfoParams):
    pass

# Below is post endpoints related functions
async def create_ticket(params: CreateTicketParams):
    ticket = params.ticket
    
    # first check if the ticket is already created
    res = await client.find_one(collection, {"ticket_id": ticket.ticket_id})
    if res:
        raise HTTPException(status_code=400, detail=f"Ticket already created with id: `{ticket.ticket_id}`")

    # post ticket
    if isinstance(ticket, PostTicket):
        res = await client.insert_one(collection, ticket.model_dump())
    elif isinstance(ticket, EditTicket):
        pass
    elif isinstance(ticket, DeleteTicket):
        pass
    
    return {
        "inserted_id": res
    }









