from fastapi import APIRouter, HTTPException

from app.auth.services import create_api_key

router = APIRouter()


# @router.post("/create")
async def create_api_key_route(name: str):
    inputs = {"name": name}
    try:
        res = await create_api_key(**inputs)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error when creating api key: {e}")
