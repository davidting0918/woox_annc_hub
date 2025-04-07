import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/chats"

# API key and secret
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Common headers for all requests
HEADERS = {
    "X-API-KEY": API_KEY,
    "X-API-SECRET": API_SECRET
}

async def test_get_chat_info_route():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/info", headers=HEADERS)
        print("GET /info:", response.json())

async def test_update_dashboard_route(direction):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/update_dashboard", params={"direction": direction}, headers=HEADERS)
        print("GET /update_dashboard:", response.json())

async def test_create_chat_route(chat_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/create", json=chat_data, headers=HEADERS)
        print("POST /create:", response.json())

async def test_update_chat_route(update_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/update", json=update_params, headers=HEADERS)
        print("POST /update:", response.json())

async def test_delete_chat_route(delete_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/delete", json=delete_params, headers=HEADERS)
        print("POST /delete:", response.json())

# Example usage
async def main():
    await test_get_chat_info_route()
    await test_update_dashboard_route("push")
    # await test_create_chat_route({
    #     "chat_id": "-4761129784",
    #     "name": "prod_test_annc",
    #     "chat_type": "group",
    #     "language": ["english", "chinese"],
    #     "category": ["test_channel"],
    #     "label": ["prd_test"],
    #     "active": True
    # })
    # await test_update_dashboard_route("push")

    # await test_update_chat_route({
    #     "chat_id": "new_chat_id",
    #     "name": "Updated Chat",
    #     "chat_type": "group",
    #     "language": ["en"],
    #     "category": ["general"],
    #     "label": ["test"],
    #     "active": True
    # })
    # await test_delete_chat_route({"chat_id": "new_chat_id"})

# Run the tests
if __name__ == "__main__":
    asyncio.run(main()) 