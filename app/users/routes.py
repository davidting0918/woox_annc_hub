# users/routes.py
from fastapi import APIRouter, HTTPException, Body, Query
from typing import Optional
from app.users.models import User, UserInfoParams, UpdateUsersInfoParams, DeleteUserParams
from app.users.services import create_user, list_users_info, update_users_info, delete_user

router = APIRouter()


# below are get routes

# list users information by params
@router.get("/info")
async def get_users_info(
    user_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    admin: Optional[bool] = Query(None),
    whitelist: Optional[bool] = Query(None),
    num: Optional[int] = Query(100)
):
    params = UserInfoParams(
        user_id=user_id,
        name=name,
        admin=admin,
        whitelist=whitelist,
        num=num
    )
    try:
        res = await list_users_info(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")


# below are post routes
@router.post("/create")
async def create_user_route(user: User = Body(...)):
    try:
        res = await create_user(user)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.post("/delete")
async def delete_user_route(params: DeleteUserParams = Body(...)):
    try:
        res = await delete_user(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.post("/update")
async def update_user_info_route(params: UpdateUsersInfoParams = Body(...)):
    try:
        res = await update_users_info(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating permission: {str(e)}")
