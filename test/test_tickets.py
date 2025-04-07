import asyncio
import httpx
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/tickets"

# API key and secret
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Common headers for all requests
HEADERS = {
    "X-API-KEY": API_KEY,
    "X-API-SECRET": API_SECRET
}

async def test_pending_tickets():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/info", headers=HEADERS, params={"status": "pending"})
        res = response.json()
        tickets = res["data"]
        pending_tickets = []
        for ticket in tickets:
            # Convert the Unix timestamp to a datetime object
            created_time = datetime.datetime.fromtimestamp(float(ticket["created_timestamp"]/1000))
            format_created_time = created_time.strftime("%Y-%m-%d %H:%M:%S")
            # Calculate the time difference
            time_diff = datetime.datetime.now() - created_time
            ticket['format_created_time'] = format_created_time
            ticket['title'] = ticket['content_text'].split('\n')[0]
            # Check if the ticket is older than 15 minutes and less than 1 day
            if datetime.timedelta(minutes=15) < time_diff < datetime.timedelta(days=1):
                pending_tickets.append(ticket)
        
        alert_message = "*Pending Tickets Alert:*\n"
        for index, ticket in enumerate(pending_tickets, start=1):
            alert_message += (
                f"{index}. Ticket ID: {ticket['ticket_id']}\n"
                f"   Create Time: {ticket['format_created_time']}\n"
                f"   Creator: {ticket['creator_name']}\n"
                f"   Title: {ticket['title']}\n"
            )
        alert_message += "@Ryenliu_WG @vy_WG @khanh_WG @AlanNguyen_WG @Karol_WG @AndyYong_WG"
        print(alert_message)

async def test_get_ticket_info_route():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/info", headers=HEADERS, params={"status": "pending"})
        res = response.json()
        print(res)
        # print("GET /info:", response.json())

async def test_update_dashboard_route():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/update_dashboard", headers=HEADERS)
        print("GET /update_dashboard:", response.json())

async def test_create_ticket_route(ticket_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/create", json=ticket_data, headers=HEADERS)
        print("POST /create:", response.json())

async def test_approve_ticket_route(approve_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/approve", json=approve_params, headers=HEADERS)
        print("POST /approve:", response.json())

async def test_reject_ticket_route(reject_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/reject", json=reject_params, headers=HEADERS)
        print("POST /reject:", response.json())

async def test_delete_ticket_route(delete_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/delete", json=delete_params, headers=HEADERS)
        print("POST /delete:", response.json())

# Example usage
async def main():
    await test_pending_tickets()
    # await test_get_ticket_info_route()
    # await test_update_dashboard_route()
    # await test_create_ticket_route({
    #     "ticket_id": "new_ticket_id",
    #     "creator_id": "creator_id",
    #     "description": "Test ticket",
    #     "status": "open"
    # })
    # await test_approve_ticket_route({
    #     "ticket_id": "new_ticket_id",
    #     "user_id": "approver_id"
    # })
    # await test_reject_ticket_route({
    #     "ticket_id": "new_ticket_id",
    #     "user_id": "rejector_id"
    # })
    # await test_delete_ticket_route({
    #     "ticket_id": "new_ticket_id"
    # })

# Run the tests
if __name__ == "__main__":
    asyncio.run(main())