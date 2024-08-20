import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestUsersRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_users_info(self):
        print("test_get_users_info")
        res = self.client.get("/users/info")
        return

if __name__ == "__main__":
    unittest.main()