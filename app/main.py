# app/main.py
from app.users.routes import router as users_router
from fastapi import FastAPI
import uvicorn

app = FastAPI()

app.include_router(users_router, prefix="/users")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)














