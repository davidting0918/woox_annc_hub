# app/main.py
from app.users.routes import router as users_router
from app.chat_info.routes import router as chat_info_router
from app.tickets.routes import router as tickets_router
from fastapi import FastAPI
import uvicorn

app = FastAPI()

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(chat_info_router, prefix="/chats", tags=["Chats"])
app.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)














