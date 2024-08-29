# app/main.py
import uvicorn
from fastapi import FastAPI

from app.auth.routes import router as auth_router
from app.chat_info.routes import router as chat_info_router
from app.tickets.routes import router as tickets_router
from app.users.routes import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(chat_info_router, prefix="/chats", tags=["Chats"])
app.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
