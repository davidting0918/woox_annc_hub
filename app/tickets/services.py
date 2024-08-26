from fastapi import HTTPException

from app.config.setting import settings
from app.db.database import MongoClient
from app.tickets.models import (
    CreateTicketParams,
    DeleteTicket,
    EditTicket,
    PostTicket,
    TicketInfoParams,
    UpdateTicketParams,
)

client = MongoClient(settings.db_name)
collection = "ticket_records"


# Below is get endpoints related functions
async def get_ticket_info(params: TicketInfoParams):
    """
    Search logic as below:
    1. ticket_id will return only one ticket
    2. other params can be independent existing and results will sort in created_timestamp descending order
    """
    if params.ticket_id:
        res = await client.find_one(collection, {"ticket_id": params.ticket_id})

    query = {}
    if params.creator_id:
        query["creator_id"] = params.creator_id

    # use created_timestamp to filter the tickets
    if params.start_created_timestamp and params.end_created_timestamp:
        query["created_timestamp"] = {"$gte": params.start_created_timestamp, "$lt": params.end_created_timestamp}
    if params.start_created_timestamp:
        query["created_timestamp"] = {"$gte": params.start_created_timestamp}
    if params.end_created_timestamp:
        query["created_timestamp"] = {"$lt": params.end_created_timestamp}

    # use status_changed_timestamp to filter the tickets
    if params.start_status_changed_timestamp and params.end_status_changed_timestamp:
        query["status_changed_timestamp"] = {
            "$gte": params.start_status_changed_timestamp,
            "$lt": params.end_status_changed_timestamp,
        }
    if params.start_status_changed_timestamp:
        query["status_changed_timestamp"] = {"$gte": params.start_status_changed_timestamp}
    if params.end_status_changed_timestamp:
        query["status_changed_timestamp"] = {"$lt": params.end_status_changed_timestamp}

    if params.status:
        query["status"] = params.status
    if params.action:
        query["action"] = params.action

    res = await client.find_many(collection, query, limit=params.num, sort=[("created_timestamp", -1)])
    return res


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
        res = await client.insert_one(collection, ticket.model_dump())
    elif isinstance(ticket, DeleteTicket):
        res = await client.insert_one(collection, ticket.model_dump())

    return {"inserted_id": res}


async def update_post_ticket(params: UpdateTicketParams):
    # check if the ticket is already created
    ticket_data = await client.find_one(collection, {"ticket_id": params.ticket_id, "action": "post_annc"})
    if not ticket_data:
        raise HTTPException(status_code=400, detail=f"Ticket not found with id: `{params.ticket_id}`")

    if params.ticket_id != params.ticket.ticket_id:
        raise HTTPException(
            status_code=400,
            detail=f"Ticket id in url and body does not match. Ticket id in url: `{params.ticket_id}`, Ticket id in body: `{params.ticket.ticket_id}`",
        )

    ticket = PostTicket(**ticket_data)
    ticket.update(**params.ticket.model_dump())
    return await client.update_one(collection, query={"ticket_id": params.ticket_id}, update=ticket.model_dump())
