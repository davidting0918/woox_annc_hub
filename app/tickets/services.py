# app/tickets/services.py
import pandas as pd
from fastapi import HTTPException

from app.config.setting import settings as s
from app.db.dashboard import GCClient
from app.db.database import MongoClient
from app.tickets.models import (
    CreateTicketParams,
    DeleteTicket,
    DeleteTicketParams,
    EditTicket,
    PostTicket,
    TicketAction,
    TicketInfoParams,
)
from app.users.models import User
from app.users.services import collection as user_collection

client = MongoClient(s.dev_db if s.is_test else s.prod_db)
collection = "ticket_records"
gc_client = GCClient()


# Below is get endpoints related functions
async def get_ticket_info(params: TicketInfoParams):
    """
    Search logic as below:
    1. ticket_id will return only one ticket
    2. other params can be independent existing and results will sort in created_timestamp descending order
    """
    if params.ticket_id:
        res = await client.find_one(collection, {"ticket_id": params.ticket_id})
        return [res] if res else []

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

    ticket_type = {
        TicketAction.post_annc: PostTicket,
        TicketAction.edit_annc: EditTicket,
        TicketAction.delete_annc: DeleteTicket,
    }
    ticket = ticket_type[params.action](**params.ticket)

    # first check if the ticket is already created
    res = await client.find_one(collection, {"ticket_id": ticket.ticket_id})
    if res:
        raise HTTPException(status_code=400, detail=f"Ticket already created with id: `{ticket.ticket_id}`")

    return await client.insert_one(collection, ticket.model_dump())


async def delete_ticket(params: DeleteTicketParams):
    status = await client.delete_one(collection, query={"ticket_id": params.ticket_id})
    return {"delete_status": status}


async def approve_ticket(ticket_id: str, user_id: str):
    """
    1. check ticket_id exists
    2. check ticket status is pending
    3. then approve the ticket
    """
    query = {"ticket_id": ticket_id}
    ticket_data = await client.find_one(collection, query)
    if not ticket_data:
        raise HTTPException(status_code=400, detail=f"Ticket not found with id: `{ticket_id}`")

    if ticket_data["status"] != "pending":
        raise HTTPException(
            status_code=400, detail=f"Ticket with id `{ticket_id}` is not in pending status: {ticket_data['status']}"
        )

    ticket_type = {
        "post_annc": PostTicket,
        "edit_annc": EditTicket,
        "delete_annc": DeleteTicket,
    }
    ticket = ticket_type[ticket_data["action"]](**ticket_data)
    user_data = await client.find_one(user_collection, {"user_id": user_id})
    if not user_data["admin"]:
        raise HTTPException(status_code=400, detail=f"User with id `{user_id}` is not admin")
    try:
        await ticket.approve(user=User(**user_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error approving ticket: {str(e)}")

    res = await client.update_one(
        collection,
        query={"ticket_id": ticket_id},
        update=ticket.model_dump(),
    )
    return res


async def reject_ticket(ticket_id: str, user_id: str):
    """
    1. check ticket_id exists
    2. check ticket status is pending
    3. then reject the ticket
    """
    params = {"ticket_id": ticket_id}
    ticket_data = await client.find_one(collection, params)
    if not ticket_data:
        raise HTTPException(status_code=400, detail=f"Ticket not found with id: `{ticket_id}`")

    if ticket_data["status"] != "pending":
        raise HTTPException(
            status_code=400, detail=f"Ticket with id `{ticket_id}` is not in pending status: {ticket_data['status']}"
        )

    ticket_type = {
        "post_annc": PostTicket,
        "edit_annc": EditTicket,
        "delete_annc": DeleteTicket,
    }
    ticket = ticket_type[ticket_data["action"]](**ticket_data)
    user_data = await client.find_one(user_collection, {"user_id": user_id})
    if not user_data["admin"]:
        raise HTTPException(status_code=400, detail=f"User with id `{user_id}` is not admin")
    ticket.reject(user=User(**user_data))

    res = await client.update_one(
        collection,
        query={"ticket_id": ticket_id},
        update=ticket.model_dump(),
    )
    return res


async def update_ticket_dashboard():
    """
    This function will push the ticket info to the google sheet in the separated 3 sheets.
    and ticket should order by created timestamp in descending order
    """
    outputs = {
        "post_tickets": None,
        "edit_tickets": None,
        "delete_tickets": None,
    }

    # update post ticket
    columns_map = {
        "ticket_id": "ID",
        "annc_type": "Announcement Type",
        "content_text": "Content",
        "category": "Category",
        "language": "Language",
        "label": "Label",
        "creator_name": "Creator Name",
        "created_timestamp": "Created Time",
        "approver_name": "Approver Name",
        "status_changed_timestamp": "Operation Time",
        "chats": "Available Chats",
        "success_chats": "Success Chats",
        "failed_chats": "Failed Chats",
    }
    post_tickets = pd.DataFrame(
        await client.find_many(collection, query={"action": TicketAction.post_annc}, sort=[("created_timestamp", -1)])
    )
    post_tickets["created_timestamp"] = pd.to_datetime(post_tickets["created_timestamp"], unit="ms")
    post_tickets["status_changed_timestamp"] = pd.to_datetime(post_tickets["status_changed_timestamp"], unit="ms")
    post_tickets["chats"] = post_tickets["chats"].apply(lambda x: ", ".join([c["chat_name"] for c in x]))
    post_tickets["success_chats"] = post_tickets["success_chats"].apply(
        lambda x: ", ".join([c["chat_name"] for c in x])
    )
    post_tickets["failed_chats"] = post_tickets["failed_chats"].apply(lambda x: ", ".join([c["chat_name"] for c in x]))
    post_tickets = post_tickets.rename(columns=columns_map).fillna("")
    post_ws = gc_client.get_ws(name="Announcement History", to_type="ws")
    post_ws.clear()
    post_ws.set_dataframe(
        post_tickets[columns_map.values()],
        start="A1",
        copy_index=False,
        copy_head=True,
    )
    outputs["post_tickets"] = post_tickets.to_dict(orient="records")

    # update edit ticket
    # update delete ticket
    return outputs
