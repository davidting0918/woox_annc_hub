import asyncio
import os
import sys
import unittest

from dotenv import load_dotenv
from httpx import AsyncClient

from app.main import app
from app.tickets.models import Announcement, PostTicket

load_dotenv(".env.development")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTicketRoutes(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.loop = asyncio.new_event_loop()
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.headers = {"X-API-KEY": self.api_key, "X-API-SECRET": self.api_secret, "Content-Type": "application/json"}
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_create_post_ticket(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                test_annc = Announcement(
                    annc_type="text",
                    content_text="This is a test announcement",
                    content_html="<p>This is a test announcement</p>",
                    content_md="This is a test announcement",
                    category=["test"],
                    language=["en"],
                    label=["test"],
                    chats=["test-123"],
                    actual_chats=["test-123"],
                )

                test_post_ticket = PostTicket(
                    annc=test_annc,
                    action="post",
                    status="pending",
                    creator_id="test-123",
                    creator_name="test",
                )
                res = await ac.post("/tickets/post", json=test_post_ticket.model_dump(), headers=self.headers)
                print(res)
                return

        self.loop.run_until_complete(run_test())
