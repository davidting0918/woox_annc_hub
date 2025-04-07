import asyncio
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/users"

# API key and secret
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

# Common headers for all requests
HEADERS = {
    "X-API-KEY": API_KEY,
    "X-API-SECRET": API_SECRET
}

async def test_get_users_info():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/info", headers=HEADERS)
        print("GET /info:", response.json())

async def test_in_whitelist_route(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/in_whitelist", params={"user_id": user_id}, headers=HEADERS)
        print("GET /in_whitelist:", response.json())

async def test_is_admin_route(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/is_admin", params={"user_id": user_id}, headers=HEADERS)
        print("GET /is_admin:", response.json())

async def test_update_dashboard_route():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/update_dashboard", headers=HEADERS)
        print("GET /update_dashboard:", response.json())

async def test_create_user_route(user_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/create", json=user_data, headers=HEADERS)
        print("POST /create:", response.json())

async def test_delete_user_route(delete_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/delete", json=delete_params, headers=HEADERS)
        print("POST /delete:", response.json())

async def test_update_user_info_route(update_params):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/update", json=update_params, headers=HEADERS)
        print("POST /update:", response.json())

# Example usage
async def main():
    # await test_delete_user_route({"user_id": "6515844923"})
    # await test_get_users_info()
    # await test_in_whitelist_route("5323246680")
    # await test_is_admin_route("5323246680")
    await test_update_dashboard_route()
    # await test_create_user_route({
    #     "user_id": "6773139594",
    #     "name": "vy_WG",
    #     "admin": True,
    #     "whitelist": True
    # })

    # await test_update_user_info_route({
    #     "user_id": "new_user_id",
    #     "name": "Updated User",
    #     "admin": True,
    #     "whitelist": True
    # })

# Run the tests
if __name__ == "__main__":
    asyncio.run(main())