import asyncio
import os
import sys
import unittest

# from datetime import datetime as dt

# from httpx import AsyncClient

# from app.main import app
# from app.tickets.models import PostTicket

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTicketRoutes(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_create_post_ticket(self):
        async def run_test():
            pass

        self.loop.run_until_complete(run_test())
