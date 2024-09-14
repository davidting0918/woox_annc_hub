# app/main.py
from argparse import ArgumentParser

import uvicorn
from fastapi import FastAPI

from app.auth.routes import router as auth_router
from app.chat_info.routes import router as chat_info_router
from app.config.setting import settings as s
from app.tickets.routes import router as tickets_router
from app.users.routes import router as users_router


# create app
def create_app(is_test: bool = False):
    s.is_test = is_test
    app = FastAPI()

    app.include_router(users_router, prefix="/users", tags=["Users"])
    app.include_router(chat_info_router, prefix="/chats", tags=["Chats"])
    app.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])

    return app


if __name__ == "__main__":
    args = ArgumentParser("Run the FastAPI server for announcement system")
    args.add_argument("--test", action="store_true", help="Run the server in test mode", default=False)

    args = args.parse_args()
    app = create_app(args.test)
    uvicorn.run(app, host="0.0.0.0", port=8000)
