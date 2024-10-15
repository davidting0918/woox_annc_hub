import os

from lib.adaptor import AnnouncementClient as ac
from telegram import Update
from telegram.ext import (
    Application,
    ChatMemberHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from utils import get_logger, init_args


class EventBot:
    @property
    def name(self):
        return "EventBot"

    def __init__(self, bot_key: str, api_key: str, api_secret: str, is_test: bool = False):
        self.client = ac(api_key=api_key, api_secret=api_secret)
        self.bot_key = bot_key
        self.logger = get_logger(self.name)
        self.is_test = is_test

    @staticmethod
    def get_chat_status(update: Update) -> list:
        old_status = str(update.my_chat_member.old_chat_member.status)
        new_status = str(update.my_chat_member.new_chat_member.status)
        if old_status == "left" and new_status == "member":
            return "add"
        elif old_status == "member" and new_status == "left":
            return "left"
        elif old_status == "left" and new_status == "administrator":
            return "add"
        elif old_status == "administrator" and new_status == "left":
            return "left"
        else:
            return None

    @staticmethod
    def handle_operator(update: Update) -> dict:
        result = {}
        chat = update.effective_chat
        operator = update.effective_user

        if operator is None and str(chat.type) == "channel":
            return None
        else:
            result["name"] = operator.full_name
            result["id"] = operator.id
        return result

    async def chat_status_update(self, update: Update, context: ContextTypes) -> None:
        operator = self.handle_operator(update)
        status = self.get_chat_status(update)
        chat = update.effective_chat

        if not operator:
            self.logger.warning(f"Unknown operator\n{update}")
            return
        else:
            if not self.client.is_admin(user_id=str(operator["id"])):
                self.logger.warning(f"Operator {operator['name']}({operator['id']}) is not admin")
                return
        if not status:
            self.logger.warning(f"Unknown status change operated by {operator['name']}({operator['id']})\n{update}")
            return

        self.client.update_chats_dashboard(direction="pull")
        if status == "add":
            chat_data = {
                "chat_id": str(chat.id),
                "name": str(chat.title),
                "chat_type": str(chat.type),
            }
            res = self.client.create_chat(**chat_data)

        elif status == "left":
            chat_data = {"chat_id": str(chat.id), "active": False}
            res = self.client.update_chat(**chat_data)

        self.logger.info(f"Operator {operator['name']}({operator['id']}) {status} chat {chat.title}({chat.id})\n{res}")
        self.client.update_chats_dashboard(direction="push")
        return

    async def chat_title_update(self, update: Update, context: ContextTypes) -> None:
        """
        This function does not need to check permission, since the chat title can be changed by any member.
        """
        chat = update.effective_chat
        operator = self.handle_operator(update)

        # if the chat not in our DB, do nothing
        self.client.update_chats_dashboard(direction="pull")

        update_ = {
            "chat_id": str(chat.id),
            "name": str(chat.title),
        }
        res = self.client.update_chat(**update_)
        self.client.update_chats_dashboard(direction="push")
        self.logger.info(
            f"Operator {operator['name']}({operator['id']}) update chat title {chat.title}({chat.id})\n{res}"
        )
        return

    def run(self):
        self.logger.info("InfoBot is running...")
        application = Application.builder().token(self.bot_key).build()

        chat_status_handler = ChatMemberHandler(self.chat_status_update, ChatMemberHandler.MY_CHAT_MEMBER)
        chat_name_update_handler = MessageHandler(filters.StatusUpdate.NEW_CHAT_TITLE, self.chat_title_update)
        application.add_handler(chat_status_handler)
        application.add_handler(chat_name_update_handler)

        application.run_polling()


if __name__ == "__main__":
    args = init_args("EventBot")
    event_bot = EventBot(
        bot_key=os.getenv("EVENT_BOT_TOKEN"),
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
        is_test=args.test,
    )
    event_bot.run()
