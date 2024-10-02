# users/routes.py
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.auth.services import verify_api_key
from app.users.models import (
    DeleteUserParams,
    UpdateUsersInfoParams,
    User,
    UserInfoParams,
)
from app.users.services import (
    create_user,
    delete_user,
    in_whitelist,
    is_admin,
    list_users_info,
    update_user_dashboard,
    update_users_info,
)

router = APIRouter(dependencies=[Depends(verify_api_key)])

# below are get routes

# list users information by params
@router.get("/info")
async def get_users_info(
    user_id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    admin: Optional[bool] = Query(None),
    whitelist: Optional[bool] = Query(None),
    num: Optional[int] = Query(100),
):
    params = UserInfoParams(user_id=user_id, name=name, admin=admin, whitelist=whitelist, num=num)
    try:
        res = await list_users_info(params)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")


@router.get("/in_whitelist")
async def in_whitelist_route(user_id: str):
    try:
        res = await in_whitelist(user_id)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking whitelist: {str(e)}")


@router.get("/is_admin")
async def is_admin_route(user_id: str):
    try:
        res = await is_admin(user_id)
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking admin: {str(e)}")


@router.get("/update_dashboard")
async def update_dashboard_route():
    try:
        res = await update_user_dashboard()
        return {"status": 1, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating dashboard: {str(e)}")


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
