import asyncio

import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient

from app.auth.services import create_api_key
from app.config.setting import Settings
from app.db.dashboard import GCClient
from app.db.database import MongoClient
from app.main import create_app

load_dotenv()


@pytest.fixture
def test_settings():
    return Settings()


@pytest.fixture
async def test_client(test_settings):
    transport = ASGITransport(app=create_app(is_test=True))
    async with AsyncClient(base_url="http://testserver", transport=transport) as client:
        yield client


@pytest.fixture(autouse=True, scope="function")
async def clean_db(test_settings):
    client = MongoClient(test_settings.dev_db)
    await client.delete_many("permission", {})
    await client.delete_many("keys", {})
    await client.delete_many("chat_info", {})
    await client.delete_many("ticket_records", {})
    yield
    await client.close()


@pytest.fixture
async def auth_headers():
    api_key = await create_api_key(name="test_key")
    return {
        "X-API-KEY": api_key["api_key"],
        "X-API-SECRET": api_key["api_secret"],
    }


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# User related endpoint
@pytest.mark.asyncio
async def test_create_user(test_client, auth_headers, clean_db):
    user_data = {"user_id": "test_user_id", "name": "Test User", "admin": False, "whitelist": False}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    return


@pytest.mark.asyncio
async def test_check_permission_function(test_client, auth_headers, clean_db):
    user_data = {"user_id": "test_user_id", "name": "Test User", "admin": False, "whitelist": False}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    res = await test_client.get("/users/in_whitelist", params={"user_id": "test_user_id"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"] is False

    res = await test_client.get("/users/is_admin", params={"user_id": "test_user_id"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"] is False

    update_user_data = {"user_id": "test_user_id", "admin": True, "whitelist": True}
    res = await test_client.post("/users/update", json=update_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    res = await test_client.get("/users/in_whitelist", params={"user_id": "test_user_id"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]

    res = await test_client.get("/users/is_admin", params={"user_id": "test_user_id"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]
    return


@pytest.mark.asyncio
async def test_update_user_info(test_client, auth_headers, clean_db):
    # create a new user
    user_data = {"user_id": "test_user_id", "name": "Test User", "admin": False, "whitelist": False}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    update_user_data = {"user_id": "test_user_id", "name": "Updated User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/update", json=update_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["name"] == "Updated User"
    assert data["data"]["admin"] is True
    assert data["data"]["whitelist"] is True
    return


@pytest.mark.asyncio
async def test_users_info(test_client, auth_headers, clean_db):
    """
    In this test, we will create 5 new users and check
    1. query with `num` parameter
    2. query with `user_id` parameter
    """
    for i in range(5):
        user_data = {"user_id": f"test_user_id_{i}", "name": f"Test User {i}", "admin": False, "whitelist": False}
        res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data

    # query with `num` parameter
    params = {"num": 2}
    res = await test_client.get("/users/info", params=params, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 2

    # query with `user_id` parameter
    for i in range(5):
        params = {"user_id": f"test_user_id_{i}"}
        res = await test_client.get("/users/info", params=params, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data
        assert len(data["data"]) == 1

    return


@pytest.mark.asyncio
async def test_delete_users(test_client, auth_headers, clean_db):
    """
    1. First insert a test user
    2. then delete the user
    """
    user_data = {"user_id": "test_user_id", "name": "Test User", "admin": False, "whitelist": False}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    delete_data = {"user_id": "test_user_id"}
    res = await test_client.post("/users/delete", json=delete_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["delete_status"]
    return


# chat related endpoint
@pytest.mark.asyncio
async def test_create_chat(test_client, auth_headers, clean_db):
    chat_data = {
        "chat_id": "test_chat_id",
        "name": "Test Chat",
        "chat_type": "group",
        "language": ["en"],
        "category": ["test"],
        "label": ["test"],
    }
    res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    return


@pytest.mark.asyncio
async def test_update_chat_info(test_client, auth_headers, clean_db):
    chat_data = {
        "chat_id": "test_chat_id",
        "name": "Test Chat",
        "chat_type": "group",
        "language": ["en"],
        "category": ["test"],
        "label": ["test"],
    }
    res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    update_chat_data = {
        "chat_id": "test_chat_id",
        "name": "Updated Chat",
        "chat_type": "channel",
        "language": ["fr", "en"],
        "category": ["test_category_1", "test_category_2"],
        "label": ["test_label_1", "test_label_2"],
    }
    res = await test_client.post("/chats/update", json=update_chat_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["name"] == "Updated Chat"
    assert data["data"]["chat_type"] == "channel"
    assert data["data"]["language"] == ["fr", "en"]
    assert data["data"]["category"] == ["test_category_1", "test_category_2"]
    assert data["data"]["label"] == ["test_label_1", "test_label_2"]
    return


@pytest.mark.asyncio
async def test_get_chat_info(test_client, auth_headers, clean_db):
    """
    In this test, we will create 105 new chats and check
    1. query with `num` parameter
    2. query with `chat_id` parameter
    3. query with `name` parameter
    """

    chat_num = 105
    for i in range(chat_num):
        chat_data = {
            "chat_id": f"test_chat_id_{i}",
            "name": f"Test Chat {i}",
            "chat_type": "group",
            "language": ["en"],
            "category": ["test"],
            "label": ["test"],
        }
        res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data

    chat_info_param = {"num": 33}
    res = await test_client.get("/chats/info", params=chat_info_param, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 33

    res = await test_client.get("/chats/info", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 100

    chat_info_param = {"chat_id": "test_chat_id_23"}
    res = await test_client.get("/chats/info", params=chat_info_param, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 1

    chat_info_param = {"name": "Test Chat 23"}
    res = await test_client.get("/chats/info", params=chat_info_param, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 1
    return


@pytest.mark.asyncio
async def test_delete_chat(test_client, auth_headers, clean_db):
    chat_data = {
        "chat_id": "test_chat_id",
        "name": "Test Chat",
        "chat_type": "group",
        "language": ["en"],
        "category": ["test"],
        "label": ["test"],
    }
    res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    # delete data
    delete_chat_data = {"chat_id": "test_chat_id"}
    res = await test_client.post("/chats/delete", json=delete_chat_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["delete_status"]
    return


# Ticket related test
@pytest.mark.asyncio
async def test_create_post_ticket(test_client, auth_headers, clean_db):
    post_ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
        },
    }
    res = await test_client.post("/tickets/create", json=post_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    return


@pytest.mark.asyncio
async def test_approve_ticket(test_client, auth_headers, clean_db):
    """
    1. create a test user and a post ticket
    2. approve with the test user
    """
    user_data = {"user_id": "approver_user_id", "name": "Approver User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    post_ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
        },
    }
    res = await test_client.post("/tickets/create", json=post_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"

    ticket_id = data["data"]["ticket_id"]
    approve_data = {
        "ticket_id": ticket_id,
        "user_id": "approver_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == ticket_id
    assert data["data"]["status"] == "approved"
    assert data["data"]["approver_id"] == "approver_user_id"
    assert data["data"]["approver_name"] == "Approver User"
    return


async def test_reject_ticket(test_client, auth_headers, clean_db):
    """
    1. create a test user and a post ticket
    2. reject with the test user
    """
    user_data = {"user_id": "reject_user_id", "name": "Reject User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    post_ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
        },
    }
    res = await test_client.post("/tickets/create", json=post_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"

    ticket_id = data["data"]["ticket_id"]
    reject_data = {
        "ticket_id": ticket_id,
        "user_id": "reject_user_id",
    }
    res = await test_client.post("/tickets/reject", json=reject_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == ticket_id
    assert data["data"]["status"] == "rejected"
    assert data["data"]["approver_id"] == "reject_user_id"
    assert data["data"]["approver_name"] == "Reject User"
    return


@pytest.mark.asyncio
async def test_delete_ticket(test_client, auth_headers, clean_db):
    post_ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
        },
    }
    res = await test_client.post("/tickets/create", json=post_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"

    ticket_id = data["data"]["ticket_id"]
    delete_data = {"ticket_id": ticket_id}
    res = await test_client.post("/tickets/delete", json=delete_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["delete_status"]
    return


@pytest.mark.asyncio
async def test_execute_post_ticket(test_client, auth_headers, clean_db):
    """
    1. create post ticket
    2. create approve user
    3. approve the ticket
    4. check execution code
    """

    chats_data = [
        {"chat_id": "-881926759", "chat_name": "v2test10"},
        {"chat_id": "-690886544", "chat_name": "v2test7"},
        {"chat_id": "-944613232", "chat_name": "v2test8"},
    ]
    error_chats_data = [
        {"chat_id": "-------", "chat_name": "error_chat"},
        {"chat_id": "--------", "chat_name": "asdfasdfasd"},
    ]
    ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "annc_type": "text",
            "content_text": "test content",
            "content_html": "<b>test content</b>",
            "content_md": "**test content**",
            "chats": chats_data + error_chats_data,
        },
    }
    res = await test_client.post("/tickets/create", json=ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"
    ticket_id = data["data"]["ticket_id"]

    approve_user_data = {"user_id": "approve_user_id", "name": "Approve User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=approve_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    approve_ticket_params = {"ticket_id": ticket_id, "user_id": "approve_user_id"}
    res = await test_client.post("/tickets/approve", json=approve_ticket_params, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == ticket_id
    assert data["data"]["status"] == "approved"
    assert data["data"]["approver_id"] == "approve_user_id"
    assert data["data"]["approver_name"] == "Approve User"
    assert data["data"]["status_changed_timestamp"]
    assert len(data["data"]["chats"]) == len(chats_data) + len(error_chats_data)
    assert len(data["data"]["success_chats"]) == len(chats_data)
    assert len(data["data"]["failed_chats"]) == len(error_chats_data)
    return


# test update dashboard information part
@pytest.mark.asyncio
async def test_update_user_dashboard_info(test_client, auth_headers, clean_db):
    """
    1. create 5 users
    2. update dashboard
    """
    for i in range(5):
        user_data = {"user_id": f"test_user_id_{i}", "name": f"Test User {i}", "admin": True, "whitelist": True}
        res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data

    res = await test_client.get("/users/update_dashboard", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 5
    return


# test update chat info dashboard
async def test_push_chat_info_dashboard(test_client, auth_headers, clean_db):
    """
    1. create 5 chats
    2. update dashboard
    """
    for i in range(5):
        chat_data = {
            "chat_id": f"test_chat_id_{i}",
            "name": f"Test Chat {i}",
            "chat_type": "group",
            "language": ["en"],
            "category": [f"test_channel_{i}", f"test_channel_{i+1}"],
            "label": ["test_label_1", "test_label_2", "test_label_3"],
        }
        res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data

    res = await test_client.get("/chats/update_dashboard", headers=auth_headers, params={"direction": "push"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == 5
    return


@pytest.mark.asyncio
async def test_pull_chat_info_dashboard(test_client, auth_headers, clean_db):
    """
    THis test will test to add a new category after pushing the chat info data.
    1. create 10 chats and push the data to the dashboard
    2. use the pygsheet to add a new category to the db
    3. run pull dashboard to update the dashboard
    4. use get chat info to test whether the new category is added or not
    """
    chat_num = 10
    for i in range(chat_num):
        chat_data = {
            "chat_id": f"test_chat_id_{i}",
            "name": f"Test Chat {i}",
            "chat_type": "group",
            "language": ["en"],
            "category": [f"test_channel_{i}", f"test_channel_{i+1}"],
            "label": ["test_label_1", "test_label_2", "test_label_3"],
        }
        res = await test_client.post("/chats/create", json=chat_data, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == 1
        assert "data" in data

    res = await test_client.get("/chats/update_dashboard", headers=auth_headers, params={"direction": "push"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == chat_num

    gc_client = GCClient()
    ws = gc_client.get_ws("TG Chat Info", to_type="ws")
    chat_info = ws.get_as_df()
    chat_info["New Pull Category"] = "V"
    chat_info["Description"] = ""
    chat_info["Label"] = "New Pull Label 1, New Pull Label 2"
    ws.clear()
    ws.set_dataframe(chat_info, (1, 1))

    res = await test_client.get("/chats/update_dashboard", headers=auth_headers, params={"direction": "pull"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert len(data["data"]) == chat_num
    assert "new_pull_category" in data["data"][0]["category"]
    assert "New Pull Label 1" in data["data"][0]["label"]
    return


async def test_update_ticket_info(test_client, auth_headers, clean_db):
    """
    This test will try to create and execute a post ticket and update the ticket info the online dashboard
    1. create a post ticket (use test_image.jpg)
    2. approve the ticket
    3. update the ticket info
    """

    chats_data = [
        {"chat_id": "-881926759", "chat_name": "v2test10"},
        {"chat_id": "-690886544", "chat_name": "v2test7"},
        {"chat_id": "-944613232", "chat_name": "v2test8"},
    ]
    error_chats_data = [
        {"chat_id": "-------", "chat_name": "error_chat"},
        {"chat_id": "--------", "chat_name": "asdfasdfasd"},
    ]
    ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "annc_type": "image",
            "content_text": "test content",
            "content_html": "<b>test content</b>",
            "content_md": "**test content**",
            "file_path": "test_image.jpg",
            "chats": chats_data + error_chats_data,
        },
    }
    res = await test_client.post("/tickets/create", json=ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"
    ticket_id = data["data"]["ticket_id"]

    approve_user_data = {"user_id": "approve_user_id", "name": "Approve User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=approve_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    approve_data = {
        "ticket_id": ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200

    # update ticket info to the dashboard
    res = await test_client.get("/tickets/update_dashboard", headers=auth_headers)
    assert res.status_code == 200
    return


async def test_execute_edit_ticket(test_client, auth_headers, clean_db):
    """
    This test will cover the following steps:
    1. create a post ticket
    2. approve the ticket
    3. create an edit ticket
    4. approve the edit ticket
    """
    chats_data = [
        {"chat_id": "-881926759", "chat_name": "v2test10"},
        {"chat_id": "-690886544", "chat_name": "v2test7"},
        {"chat_id": "-944613232", "chat_name": "v2test8"},
    ]
    error_chats_data = [
        {"chat_id": "-------", "chat_name": "error_chat"},
        {"chat_id": "--------", "chat_name": "asdfasdfasd"},
    ]
    ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "annc_type": "image",
            "content_text": "test content",
            "content_html": "<b>test content</b>",
            "content_md": "**test content**",
            "file_path": "test_image.jpg",
            "chats": chats_data + error_chats_data,
        },
    }
    res = await test_client.post("/tickets/create", json=ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"
    ticket_id = data["data"]["ticket_id"]

    approve_user_data = {"user_id": "approve_user_id", "name": "Approve User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=approve_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    approve_data = {
        "ticket_id": ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200

    edit_ticket_data = {
        "action": "edit_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "old_ticket_id": ticket_id,
            "new_content_text": "new test content",
            "new_content_html": "<b>new test content</b>",
            "new_content_md": "**new test content**",
        },
    }
    res = await test_client.post("/tickets/create", json=edit_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "edit_annc"
    edit_ticket_id = data["data"]["ticket_id"]

    approve_data = {
        "ticket_id": edit_ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == edit_ticket_id
    assert data["data"]["status"] == "approved"
    assert data["data"]["approver_id"] == "approve_user_id"
    assert data["data"]["approver_name"] == "Approve User"
    assert len(data["data"]["success_chats"]) == len(chats_data)

    # update ticket info to the dashboard
    res = await test_client.get("/tickets/update_dashboard", headers=auth_headers)
    assert res.status_code == 200
    return


async def test_execute_all_ticket_and_update_dashboard(test_client, auth_headers, clean_db):
    """
    This test will cover the following steps:
    1. create a post ticket
    2. approve the ticket
    3. create an edit ticket
    4. approve the edit ticket
    5. create a delete ticket
    6. approve the delete ticket
    """
    chats_data = [
        {"chat_id": "-881926759", "chat_name": "v2test10"},
        {"chat_id": "-690886544", "chat_name": "v2test7"},
        {"chat_id": "-944613232", "chat_name": "v2test8"},
    ]
    error_chats_data = [
        {"chat_id": "-------", "chat_name": "error_chat"},
        {"chat_id": "--------", "chat_name": "asdfasdfasd"},
    ]
    ticket_data = {
        "action": "post_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "annc_type": "image",
            "content_text": "test content",
            "content_html": "<b>test content</b>",
            "content_md": "**test content**",
            "file_path": "test_image.jpg",
            "chats": chats_data + error_chats_data,
        },
    }
    res = await test_client.post("/tickets/create", json=ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "post_annc"
    ticket_id = data["data"]["ticket_id"]

    approve_user_data = {"user_id": "approve_user_id", "name": "Approve User", "admin": True, "whitelist": True}
    res = await test_client.post("/users/create", json=approve_user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data

    approve_data = {
        "ticket_id": ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200

    edit_ticket_data = {
        "action": "edit_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "old_ticket_id": ticket_id,
            "new_content_text": "new test content",
            "new_content_html": "<b>new test content</b>",
            "new_content_md": "**new test content**",
        },
    }
    res = await test_client.post("/tickets/create", json=edit_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "edit_annc"
    edit_ticket_id = data["data"]["ticket_id"]

    approve_data = {
        "ticket_id": edit_ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == edit_ticket_id
    assert data["data"]["status"] == "approved"
    assert data["data"]["approver_id"] == "approve_user_id"
    assert data["data"]["approver_name"] == "Approve User"
    assert len(data["data"]["success_chats"]) == len(chats_data)

    # create delete ticket
    delete_ticket_data = {
        "action": "delete_annc",
        "ticket": {
            "creator_id": "test_user_id",
            "creator_name": "Test User",
            "old_ticket_id": ticket_id,
        },
    }
    res = await test_client.post("/tickets/create", json=delete_ticket_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"]
    assert data["data"]["status"] == "pending"
    assert data["data"]["action"] == "delete_annc"
    delete_ticket_id = data["data"]["ticket_id"]

    approve_data = {
        "ticket_id": delete_ticket_id,
        "user_id": "approve_user_id",
    }
    res = await test_client.post("/tickets/approve", json=approve_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    assert data["data"]["ticket_id"] == delete_ticket_id
    assert data["data"]["status"] == "approved"
    assert data["data"]["approver_id"] == "approve_user_id"

    # update ticket info to the dashboard
    res = await test_client.get("/tickets/update_dashboard", headers=auth_headers)
    assert res.status_code == 200
    return
