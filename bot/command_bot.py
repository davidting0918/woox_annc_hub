import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler
from utils import get_logger

from bot.lib.adaptor import AnnouncementClient as ac

CATEGORY, LANGUAGE, LABEL, CONTENT = range(4)


class CommandBot:
    @property
    def name(self):
        return "CommandBot"

    def __init__(self, command_bot_key: str, api_key: str, api_secret: str):
        self.client = ac(api_key=api_key, api_secret=api_secret)
        self.command_bot_key = command_bot_key
        self.logger = get_logger(self.name)

    async def start(self, update: Update, context: ContextTypes) -> None:
        res = self.client.in_whitelist(user_id=str(update.message.from_user.id))
        if res["data"]:
            await update.message.reply_text("Hello! I'm the command bot.")

    """
    post new announcement pipeline:
    post -> choose_category -> choose_language -> choose_label -> input_content
    """

    async def post(self, update: Update, context: ContextTypes) -> int:
        operator = update.message.from_user

        if not self.client.in_whitelist(user_id=str(operator.id))["data"]:
            await update.message.reply_text(f"Hi {operator.full_name}, You are not in the whitelist")
            return ConversationHandler.END

        res = self.client.update_chats_dashboard(direction="pull")

        # Create category button, two choice per row
        category = list(set([j for i in res["data"] for j in i["category"]]))
        name_callback = [(i.replace("_", " ").title(), i) for i in category]
        name_callback.append(("Others", "others"))

        keyboard = []
        for i in range(len(name_callback)):
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(name_callback[i][0], callback_data=name_callback[i][1])])
            else:
                keyboard[-1].append(InlineKeyboardButton(name_callback[i][0], callback_data=name_callback[i][1]))
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"Hello {operator.full_name}! Please choose a category for your post."

        await update.message.reply_text(message, reply_markup=reply_markup)

        # create annc ticket
        params = {
            "action": "post_annc",
            "ticket": {
                "creator_id": str(operator.id),
                "creator_name": str(operator.full_name),
            },
        }
        res = self.client.create_ticket(**params)
        context.user_data["ticket_id"] = res["data"]["ticket_id"]
        self.logger.info(f"Ticket created with params: {params}, ticket_id: {res['data']['ticket_id']}")
        return CATEGORY

    async def choose_category(self, update: Update, context: ContextTypes) -> int:
        query = update.callback_query
        context.user_data["category"] = query.data

        if query.data == "others":
            message = (
                f"You have chosen \n"
                f"**Category** : `{query.data.replace('_', ' ').title()}`\n"
                f"Please enter the labels or names of the chats you want to post, each label per line\n"
            )
            await query.message.edit_text(message, parse_mode="MarkdownV2")

            return LABEL
        else:
            keyboard = [
                [InlineKeyboardButton("English", callback_data="english")],
                [InlineKeyboardButton("Chinese", callback_data="chinese")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = (
                f"You have chosen \n"
                f"**Category** : `{query.data.replace('_', ' ').title()}`\n"
                f"Please choose a language for your post"
            )
            await query.message.edit_text(message, reply_markup=reply_markup, parse_mode="MarkdownV2")

            return LANGUAGE

    async def choose_language(self, update: Update, context: ContextTypes) -> int:
        query = update.callback_query
        context.user_data["language"] = query.data

        message = (
            f"You have chosen \n"
            f"**Category** : `{context.user_data['category'].replace('_', ' ').title()}`\n"
            f"**Language** : `{context.user_data['language'].title()}`\n"
            f"Please enter the content of your post, in text, photo, video or document format\n"
        )
        await query.message.edit_text(message, parse_mode="MarkdownV2")
        return CONTENT

    async def choose_label(self, update: Update, context: ContextTypes) -> int:
        text = update.message.text
        labels_or_names = [i.strip() for i in text.split("\n") if i.strip() != ""]

        labels = []
        names = []

        chats = self.client.get_chat_info(active=True, num=500)["data"]
        distinct_labels = list(set([j for i in chats for j in i["label"]]))
        distinct_names = list(set([i["name"] for i in chats]))

        for i in labels_or_names:
            if i in distinct_labels:
                labels.append(i)
            elif i in distinct_names:
                names.append(i)
            else:
                if i in ["/cancel", "/cancel@WOO_Announcement_Request_Bot"]:
                    await self.cancel(update, context)
                    return ConversationHandler.END
                await update.message.reply_text(
                    f"Label or name `{i}` not found, please check again", parse_mode="MarkdownV2"
                )
                return LABEL

        context.user_data["labels"] = labels
        context.user_data["chats"] = names

        message = (
            f"You have chosen \n"
            f"**Category** : `{context.user_data['category'].replace('_', ' ').title()}`\n"
            f"**Labels** : `{', '.join(labels)}`\n"
            f"**Chats** : `{', '.join(names)}`\n"
            f"Please enter the content of your post, in text, photo or video format\n"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2")
        return CONTENT

    async def input_content(self, update: Update, context: ContextTypes) -> None:
        return

    async def cancel(self, update: Update, context: ContextTypes) -> int:
        operator = update.message.from_user

        message = f"Bye {operator.full_name}! I hope we can talk again some day."

        await update.message.reply_text(message)
        return ConversationHandler.END

    def run(self) -> None:
        self.logger.info(f"Starting {self.name}...")
        app = Application.builder().token(self.command_bot_key).build()

        app.add_handler(CommandHandler("start", self.start))

        app.run_polling()


if __name__ == "__main__":
    load_dotenv()
    bot = CommandBot(
        command_bot_key=os.getenv("COMMAND_BOT_TOKEN"),
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
    )
    bot.run()
