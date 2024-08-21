import unittest
import asyncio
from httpx import AsyncClient
from datetime import datetime as dt
from app.main import app  # Assuming your FastAPI app is in app.main
from app.users.models import User, DeleteUserParams

class TestUsersRoutes(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_create_user(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                # testing user creation
                user_id = f"test-{str(int(dt.now().timestamp()))}"
                user = User(
                    user_id=user_id,
                    name="test",
                    admin=False,
                    whitelist=False
                )
                res = await ac.post("/users/create", json=user.model_dump())
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                data = res.json()
                self.assertEqual(data['status'], 1)

                # testing user deletion
                delete_params = DeleteUserParams(
                    user_id=user_id
                )
                res = await ac.post("/users/delete", json=delete_params.model_dump())
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")

                data = res.json()
                self.assertEqual(data['status'], 1)
                self.assertEqual(data['data']['delete_status'], True)
        self.loop.run_until_complete(run_test())
