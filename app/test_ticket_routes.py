import asyncio
import os
import sys
import unittest

from dotenv import load_dotenv
from httpx import AsyncClient

from app.main import app
from app.tickets.models import (
    Announcement,
    ApproveRejectParams,
    CreateTicketParams,
    DeleteTicketParams,
    PostTicket,
)

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
                # test create a new ticket in the db
                test_annc = Announcement(
                    annc_type="text",
                    content_text="This is a test announcement",
                    content_html="<p>This is a test announcement</p>",
                    content_md="This is a test announcement",
                    category="test",
                    language="en",
                    label=["test"],
                    chats=["test-123"],
                    actual_chats=["test-123"],
                )

                test_post_ticket = PostTicket(
                    annc=test_annc,
                    action="post_annc",
                    status="pending",
                    creator_id="test-123",
                    creator_name="test",
                )

                params = CreateTicketParams(ticket=test_post_ticket)
                ticket_id = params.ticket.ticket_id
                res = await ac.post("/tickets/create", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["status"], 1)

                # test delete the ticket in the db
                params = DeleteTicketParams(ticket_id=ticket_id)
                res = await ac.post("/tickets/delete", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["data"]["delete_status"], True)

                return

        self.loop.run_until_complete(run_test())

    def test_approve_ticket(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                # test create a new ticket in the db
                test_annc = Announcement(
                    annc_type="text",
                    content_text="This is a test announcement",
                    content_html="<p>This is a test announcement</p>",
                    content_md="This is a test announcement",
                    category="test",
                    language="en",
                    label=["test"],
                    chats=["test-123"],
                    actual_chats=["test-123"],
                )

                test_post_ticket = PostTicket(
                    annc=test_annc,
                    action="post_annc",
                    status="pending",
                    creator_id="test-123",
                    creator_name="test",
                )

                params = CreateTicketParams(ticket=test_post_ticket)
                ticket_id = params.ticket.ticket_id
                res = await ac.post("/tickets/create", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["status"], 1)

                # test approve
                params = ApproveRejectParams(ticket_id=ticket_id, user_id="dev-test")
                res = await ac.post("/tickets/approve", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["status"], "approved")

                # test delete the ticket in the db
                params = DeleteTicketParams(ticket_id=ticket_id)
                res = await ac.post("/tickets/delete", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["data"]["delete_status"], True)

                return

        self.loop.run_until_complete(run_test())

    def test_reject_ticket(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as ac:
                # test create a new ticket in the db
                test_annc = Announcement(
                    annc_type="text",
                    content_text="This is a test announcement",
                    content_html="<p>This is a test announcement</p>",
                    content_md="This is a test announcement",
                    category="test",
                    language="en",
                    label=["test"],
                    chats=["test-123"],
                    actual_chats=["test-123"],
                )

                test_post_ticket = PostTicket(
                    annc=test_annc,
                    action="post_annc",
                    status="pending",
                    creator_id="test-123",
                    creator_name="test",
                )

                params = CreateTicketParams(ticket=test_post_ticket)
                ticket_id = params.ticket.ticket_id
                res = await ac.post("/tickets/create", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["status"], 1)

                # test approve
                params = ApproveRejectParams(ticket_id=ticket_id, user_id="dev-test")
                res = await ac.post("/tickets/reject", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["status"], "approved")

                # test delete the ticket in the db
                params = DeleteTicketParams(ticket_id=ticket_id)
                res = await ac.post("/tickets/delete", json=params.model_dump(), headers=self.headers)
                self.assertEqual(res.status_code, 200, f"Response: {res.json()}")
                data = res.json()
                self.assertEqual(data["data"]["delete_status"], True)

                return

        self.loop.run_until_complete(run_test())
