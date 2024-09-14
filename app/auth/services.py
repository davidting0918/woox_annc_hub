import secrets

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.auth.models import APIKey
from app.config.setting import settings as s
from app.db.database import MongoClient

client = MongoClient(s.dev_db if s.is_test else s.prod_db)
collections = "keys"

API_KEY_HEADER = APIKeyHeader(name="X-API-KEY")
API_SECRET_HEADER = APIKeyHeader(name="X-API-SECRET")


async def create_api_key(name: str) -> APIKey:

    # check whether the key name is already exists
    res = await client.find_one(collections, query={"name": name})
    if res:
        raise HTTPException(status_code=400, detail=f"Key name already exists with name: `{name}`")

    api_key = secrets.token_hex(16)
    api_secret = secrets.token_hex(32)
    key = APIKey(api_key=api_key, api_secret=api_secret, name=name)
    await client.insert_one(collections, key.model_dump())
    return key.model_dump()


async def validate_api_key(api_key: str, api_secret: str) -> bool:
    key = await client.find_one(collections, query={"api_key": api_key})
    if not key:
        return False
    if key["api_secret"] != api_secret:
        return False
    return True


async def verify_api_key(api_key: str = Security(API_KEY_HEADER), api_secret: str = Security(API_SECRET_HEADER)):

    res = await validate_api_key(api_key, api_secret)
    if not res:
        raise HTTPException(status_code=403, detail="Invalid API key or secret")
    return api_key
