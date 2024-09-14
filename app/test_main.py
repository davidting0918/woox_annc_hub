import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.services import create_api_key
from app.config.setting import Settings
from app.db.database import MongoClient
from app.main import create_app


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
@pytest.mark.asyncio(loop_scope="function")
async def test_create_user(test_client, auth_headers, clean_db):
    user_data = {"user_id": "test_user_id", "name": "Test User", "admin": False, "whitelist": False}
    res = await test_client.post("/users/create", json=user_data, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == 1
    assert "data" in data
    return


@pytest.mark.asyncio(loop_scope="function")
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
    user_data = {"user_id": "approver_user_id", "name": "Approver User", "admin": False, "whitelist": False}
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