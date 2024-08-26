import asyncio
import os
import sys
import unittest
from datetime import datetime as dt

from httpx import AsyncClient

from app.chat_info.models import Chat, ChatType, DeleteChatInfo, UpdateChatInfo
from app.main import app

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestChatRoutes(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_create_chat(self):
        async def run_test():
            async with AsyncClient(app=app, base_url=self.base_url) as client:
                # test create chat and use get chat info to check if it exists then delete it to test delete chat info
                chat_id = f"test-{str(int(dt.now().timestamp()))}"
                name = "test chat"
                chat_type = ChatType.supergroup
                language = ["en", "ch"]
                category = ["listing", "delisting", "maintenance"]
                chat = Chat(chat_id=chat_id, name=name, chat_type=chat_type, language=language, category=category)
                print(f"chat: {chat.model_dump()}")
                res = await client.post("chats/create", json=chat.model_dump())

                self.assertEqual(res.status_code, 200, res.text)
                data = res.json()
                self.assertEqual(data["status"], 1)

                # get chat info
                query_params = {"chat_id": chat_id}
                print(f"query params: {query_params}")
                res = await client.get("chats/info", params=query_params)
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["chat_id"], chat_id)
                self.assertEqual(data["data"]["name"], name)
                self.assertEqual(data["data"]["chat_type"], chat_type)
                self.assertEqual(data["data"]["language"], language)
                self.assertEqual(data["data"]["category"], category)

                # update chat info (add data)
                new_language = ["en", "ch", "jp"]
                new_category = ["listing", "delisting", "maintenance", "other"]
                label = ["label1", "label2", "label3"]
                update_chat_info = UpdateChatInfo(
                    chat_id=chat_id, language=new_language, category=new_category, label=label
                )
                print(f"update chat info: {update_chat_info.model_dump()}")
                res = await client.post("chats/update", json=update_chat_info.model_dump())
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["status"], 1)

                # delete chat info
                delete_chat_info = DeleteChatInfo(chat_id=chat_id)
                print(f"delete chat info: {delete_chat_info.model_dump()}")
                res = await client.post("chats/delete", json=delete_chat_info.model_dump())
                self.assertEqual(res.status_code, 200)
                data = res.json()
                self.assertEqual(data["status"], 1)
                self.assertEqual(data["data"]["delete_status"], True)
                return

        self.loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
