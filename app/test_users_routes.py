import asyncio
import os
import unittest
from datetime import datetime as dt

from dotenv import load_dotenv
from httpx import AsyncClient

from app.main import app  # Assuming your FastAPI app is in app.main
from app.users.models import DeleteUserParams, UpdateUsersInfoParams, User

load_dotenv(".env.development")


class TestUsersRoutes(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.loop = asyncio.new_event_loop()
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.headers = {"X-API-KEY": self.api_key, "X-API-SECRET": self.api_secret, "Content-Type": "application/json"}
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_create_and_delete_user(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                # testing user creation
                user_id = f"test-{str(int(dt.now().timestamp()))}"
                user = User(user_id=user_id, name="test", admin=False, whitelist=False)
                print(user.model_dump())
                res = await ac.post("/users/create", json=user.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                data = res.json()
                self.assertEqual(data["status"], 1)

                # testing user deletion
                delete_params = DeleteUserParams(user_id=user_id)
                res = await ac.post("/users/delete", json=delete_params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                data = res.json()
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["delete_status"], True)

        self.loop.run_until_complete(run_test())

    def test_update_user(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                user_id = f"test-{str(int(dt.now().timestamp()))}"
                user = User(user_id=user_id, name="test", admin=False, whitelist=False)
                res = await ac.post("/users/create", json=user.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                data = res.json()
                self.assertEqual(data["status"], 1)

                # test updating user
                update_params = UpdateUsersInfoParams(user_id=user_id, name="test2", admin=True, whitelist=True)
                res = await ac.post("/users/update", json=update_params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                # get user info to test whether the update is successful
                res = await ac.get(f"/users/info", params={"user_id": user_id}, headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.text}")

                data = res.json()
                user = data["data"][0]
                self.assertEqual(data["status"], 1)
                self.assertEqual(user["name"], "test2")
                self.assertEqual(user["admin"], True)
                self.assertEqual(user["whitelist"], True)

                # delete user to clean up
                delete_params = DeleteUserParams(user_id=user_id)
                res = await ac.post("/users/delete", json=delete_params.model_dump(), headers=self.headers)
                data = res.json()
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["delete_status"], True)

        self.loop.run_until_complete(run_test())
