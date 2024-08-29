import os
from unittest import TestCase

import requests as rq
from dotenv import load_dotenv

load_dotenv(".env.development")


class TestEndpoints(TestCase):
    def setUp(self):
        self.endpoint = "http://localhost:8000"

    def test_private_endpoint(self):
        key = os.getenv("API_KEY")
        secret = os.getenv("API_SECRET")

        headers = {"X-API-KEY": key, "X-API-SECRET": secret}

        response = rq.get(f"{self.endpoint}/users/info?num=100", headers=headers)
        data = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEquals(data["status"], 1)
        return
