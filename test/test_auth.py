import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/auth"

async def test_create_api_key_route(name):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/create", params={"name": name},json={})
        print("POST /create:", response.json())

# Example usage
async def main():
    await test_create_api_key_route("leondu")

# Run the test
if __name__ == "__main__":
    asyncio.run(main())