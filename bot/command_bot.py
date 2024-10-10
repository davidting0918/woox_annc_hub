import os

from dotenv import load_dotenv
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update, request
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from utils import get_logger, init_args, save_file

from bot.lib.adaptor import AnnouncementClient as ac

CATEGORY, LANGUAGE, LABEL, CONTENT = range(4)
EDIT_TICKET_ID, EDIT_NEW_CONTENT = range(2)


class CommandBot:
    REQUEST = request.HTTPXRequest(connection_pool_size=50000, connect_timeout=300, read_timeout=300)
    CONFIRM_CHAT_ID = "-836971986"  # WOO Announcement Approve
    TEST_CONFIRM_CHAT_ID = "5327851721"  # davidding_WG

    @property
    def name(self):
        return "CommandBot"

    def __init__(self, command_bot_key: str, api_key: str, api_secret: str, is_test: bool = False):
        self.client = ac(api_key=api_key, api_secret=api_secret)
        self.command_bot_key = command_bot_key
        self.logger = get_logger(self.name)
        self.is_test = is_test

    def get_confirm_message(self, ticket_id: str) -> str:
        data = self.client.get_ticket_info(ticket_id=ticket_id)["data"][0]
        if data["action"] == "post_annc":
            if data["category"] != "others":
                message = (
                    f"<b>[Confirm Message]</b>\n\n"
                    f"<b>ID:</b> <code>{ticket_id}</code>\n"
                    f"<b>Creator:</b> {data['creator_name']}\n"
                    f"<b>Category:</b> <code>{data['category'].replace('_', ' ').title()}</code>\n"
                    f"<b>Language:</b> <code>{data['language'].title()}</code>\n"
                    f"<b>Chat numbers:</b> {len(data['chats'])}\n"
                    f"<a> Please check the announcement content in the next message.</a>"
                )
            else:
                message = (
                    f"<b>[Confirm Message]</b>\n\n"
                    f"<b>ID:</b> <code>{ticket_id}</code>\n"
                    f"<b>Creator:</b> {data['creator_name']}\n"
                    f"<b>Chat numbers:</b> {len(data['chats'])}\n"
                    f"<a> Please check the announcement content in the next message.</a>"
                )
        elif data["action"] == "edit_annc":
            message = (
                f"<b>[Confirm Message]</b>\n\n"
                f"<b>ID:</b> <code>{ticket_id}</code>\n"
                f"<b>Annc ID:</b> <code>{data['old_ticket_id']}</code>\n"
                f"<b>Creator:</b> {data['creator_name']}\n"
                f"<b>Chat numbers:</b> {len(data['chats'])}\n\n"
                f"<b>Original Contents:</b>\n\n"
                f"{data['old_content_html']}\n\n"
                f"<b>New Contents:</b>\n\n"
                f"{data['new_content_html']}\n"
            )

        return message

    def get_report_message(self, ticket_id: str) -> str:
        data = self.client.get_ticket_info(ticket_id=ticket_id)["data"][0]
        if data["action"] == "post_annc":
            if data["category"] == "others":
                message = (
                    f"<b>[{'Approved' if data['status'] == 'approved' else 'Rejected'} Message]</b>\n\n"
                    f"<b>Operation:</b> <code>{data['action']}</code>\n"
                    f"<b>ID:</b> {data['ticket_id']}\n"
                    f"<b>Creator:</b> {data['creator_name']}\n"
                    f"<b>Operator:</b> {data['approver_name']}\n"
                    f"<b>Labels:</b> <code>{', '.join(data['label']) if data['label'] else ''}</code>\n"
                    f"<b>Chats:</b> <code>{', '.join([i['chat_name'] for i in data['chats']]) if data['chats'] else ''}</code>\n"
                    f"<b>Expected Chat numbers:</b> {len(data['chats']) if data['status'] == 'approved' else 0}\n"
                    f"<b>Succeed Chat numbers:</b> {len(data['success_chats'])}\n"
                    f"<b>Failed Chat numbers:</b> {len(data['failed_chats'])}\n"
                )
            else:
                message = (
                    f"<b>[{'Approved' if data['status'] == 'approved' else 'Rejected'} Message]</b>\n\n"
                    f"<b>Operation:</b> <code>{data['action']}</code>\n"
                    f"<b>ID:</b> <code>{data['ticket_id']}</code>\n"
                    f"<b>Creator:</b> {data['creator_name']}\n"
                    f"<b>Operator:</b> {data['approver_name']}\n"
                    f"<b>Category:</b> <code>{data['category'].replace('_', ' ').title()}</code>\n"
                    f"<b>Language:</b> <code>{data['language'].title()}</code>\n"
                    f"<b>Expected Chat numbers:</b> {len(data['chats']) if data['status'] == 'approved' else 0}\n"
                    f"<b>Succeed Chat numbers:</b> {len(data['success_chats'])}\n"
                    f"<b>Failed Chat numbers:</b> {len(data['failed_chats'])}\n"
                )
        elif data["action"] == "edit_annc":
            message = (
                f"<b>[{'Approved' if data['status'] == 'approved' else 'Rejected'} Message]</b>\n\n"
                f"<b>Operation:</b> <code>{data['action']}</code>\n"
                f"<b>ID:</b> <code>{data['ticket_id']}</code>\n"
                f"<b>Annc ID:</b> <code>{data['old_ticket_id']}</code>\n"
                f"<b>Creator:</b> {data['creator_name']}\n"
                f"<b>Operator:</b> {data['approver_name']}\n"
                f"<b>Chat numbers:</b> {len(data['chats'])}\n"
                f"<b>Original Contents:</b>\n\n"
                f"{data['old_content_html']}\n\n"
                f"<b>New Contents:</b>\n\n"
                f"{data['new_content_html']}\n"
            )
        return message

    def get_category_pattern(self):
        chats = self.client.get_chat_info(active=True)["data"]
        category = list(set([j for i in chats for j in i["category"]]))
        return "|".join(category) + "|others"

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
        category = sorted(list(set([j for i in res["data"] for j in i["category"]])))
        name_callback = [(i.replace("_", " ").title(), f"category_{i}") for i in category]
        name_callback.append(("Others", "category_others"))

        keyboard = []
        for i in range(len(name_callback)):
            if i % 2 == 0:
                keyboard.append([InlineKeyboardButton(name_callback[i][0], callback_data=name_callback[i][1])])
            else:
                keyboard[-1].append(InlineKeyboardButton(name_callback[i][0], callback_data=name_callback[i][1]))
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = f"Hello {operator.full_name}! Please choose a category for your post."

        await update.message.reply_text(message, reply_markup=reply_markup)

        # store announcement info in context user_data
        context.user_data["creator_id"] = str(operator.id)
        context.user_data["creator_name"] = operator.full_name
        return CATEGORY

    async def choose_category(self, update: Update, context: ContextTypes) -> int:
        query = update.callback_query
        category = query.data.replace("category_", "")  # to skip prefix
        context.user_data["category"] = category

        if category == "others":
            message = (
                f"You have chosen \n"
                f"**Category** : `{category.replace('_', ' ').title()}`\n"
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
                f"**Category** : `{category.replace('_', ' ').title()}`\n"
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

        chats = self.client.get_chat_info(active=True)["data"]
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
        message = update.message
        operator = update.message.from_user

        # check content type
        image = message.photo
        video = message.video
        content_text = message.caption if message.caption else message.text if message.text else ""
        content_html = message.caption_html if message.caption_html else message.text_html if message.text_html else ""
        content_md = (
            message.caption_markdown
            if message.caption_markdown
            else message.text_markdown
            if message.text_markdown
            else ""
        )

        if len(image) != 0:  # image condition
            file_id = image[3].file_id
            annc_type = "image"

        elif video is not None:  # video condition
            file_id = video.file_id
            annc_type = "video"

        else:  # Only text condition
            file_id = ""
            annc_type = "text"

        file = await save_file(file_id, bot=Bot(self.command_bot_key, request=self.REQUEST))

        # get all chats, split into 1. using category + language 2. using labels + names
        if context.user_data["category"] == "others":
            # check whether there is label or name in the input, if exist then do query
            chats = []
            if context.user_data["labels"]:
                chats += self.client.get_chat_info(label=context.user_data["labels"])["data"]

            if context.user_data["chats"]:
                chats += self.client.get_chat_info(name=context.user_data["chats"])["data"]

        else:
            chats = self.client.get_chat_info(
                category=context.user_data["category"], language=context.user_data["language"]
            )["data"]

        distinct_chats = [
            {
                "chat_id": i[0],
                "chat_name": i[1],
            }
            for i in list(
                set(
                    (
                        i["chat_id"],
                        i["name"],
                    )
                    for i in chats
                )
            )
        ]
        # combine info in context user_data and create ticket
        ticket_data = {
            "action": "post_annc",
            "ticket": {
                "creator_id": context.user_data["creator_id"],
                "creator_name": context.user_data["creator_name"],
                "annc_type": annc_type,
                "content_text": content_text,
                "content_html": content_html,
                "content_md": content_md,
                "file_path": file["path"],
                "category": context.user_data["category"],
                "language": context.user_data["language"] if context.user_data["category"] != "others" else "",
                "labels": context.user_data["labels"] if context.user_data["category"] == "others" else [],
                "chats": distinct_chats,
            },
        }
        res = self.client.create_ticket(**ticket_data)["data"]
        ticket_id = res["ticket_id"]

        method_map = {
            "image": context.bot.send_photo,
            "video": context.bot.send_video,
            "text": context.bot.send_message,
        }

        keyboard = [
            [InlineKeyboardButton("Approve", callback_data=f"approve_{ticket_id}")],
            [InlineKeyboardButton("Reject", callback_data=f"reject_{ticket_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # declare variable for confirm message
        chat_id = self.TEST_CONFIRM_CHAT_ID if self.is_test else self.CONFIRM_CHAT_ID

        # send out first part of confirm message, include confirm button
        inputs = {
            "chat_id": chat_id,
            "text": self.get_confirm_message(ticket_id),
            "parse_mode": "HTML",
            "reply_markup": reply_markup,
        }
        await context.bot.send_message(**inputs)

        # send out second part of confirm message, to check the announcement content
        if annc_type in ["image", "video"]:
            inputs = {
                "chat_id": chat_id,
                annc_type.replace("image", "photo"): file["id"],
                "caption": content_html,
                "parse_mode": "HTML",
            }

        else:
            inputs = {
                "chat_id": chat_id,
                "text": content_html,
                "parse_mode": "HTML",
            }

        await method_map[annc_type](**inputs)
        self.logger.info(f"Announcement `{ticket_id}` ticket sent by {operator.full_name}({operator.id})")

        # update local ticket info to google sheet
        self.client.update_ticket_dashboard()

        message = (
            f"Your post has been sent to the admin group for approval, "
            f"please wait patiently\.\n"
            f"ID: `{ticket_id}`"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2")

        return ConversationHandler.END

    async def confirm_post(self, update: Update, context: ContextTypes) -> None:
        operator = update.callback_query.from_user

        query = update.callback_query
        ticket_id = query.data.split("_")[1]
        action = query.data.split("_")[0]

        if action == "approve":
            self.client.approve_ticket(ticket_id=ticket_id, user_id=str(operator.id))

        else:
            self.client.reject_ticket(ticket_id=ticket_id, user_id=str(operator.id))

        report_message = self.get_report_message(ticket_id)

        await query.message.edit_text(report_message, parse_mode="HTML")
        self.client.update_ticket_dashboard()

        self.logger.info(f"Announcement `{ticket_id}` ticket {action} by {operator.full_name}({operator.id})")
        return ConversationHandler.END

    async def edit(self, update: Update, context: ContextTypes) -> None:
        operator = update.message.from_user

        if not self.client.in_whitelist(user_id=str(operator.id))["data"]:
            await update.message.reply_text(f"Hi {operator.full_name}, You are not in the whitelist")
            return ConversationHandler.END

        self.client.update_ticket_dashboard()

        message = (
            f"Hello {operator.full_name}\! Please enter the ID of the announcement you want to edit\. \n"
            f"Can check the ID in [**Announcement History**]"
            f"(https://docs.google.com/spreadsheets/d/1k2P8Ok0O6d9J3_WWDiEbmKpIkKrWYG96gB52zrEGOf0/edit?gid=0#gid=0)"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2")
        context.user_data["creator_id"] = str(operator.id)
        context.user_data["creator_name"] = operator.full_name

        return EDIT_TICKET_ID

    async def choose_edit_ticket_id(self, update: Update, context: ContextTypes) -> int:
        ticket_id = update.message.text

        res = self.client.get_ticket_info(ticket_id=ticket_id)
        if "data" not in res:
            await update.message.reply_text(f"Ticket ID `{ticket_id}` not found, please check again")
            return EDIT_TICKET_ID
        data = res["data"][0]

        if data["status"] != "approved":
            await update.message.reply_text(
                f"Ticket ID `{ticket_id}` is not approved, currently in `{data['status']}` status"
            )
            return EDIT_TICKET_ID

        context.user_data["old_ticket_id"] = ticket_id

        message = f"Ticket `{ticket_id}` found, please enter the new content of the announcement\n"
        await update.message.reply_text(message, parse_mode="MarkdownV2")
        return EDIT_NEW_CONTENT

    async def input_edit_new_content(self, update: Update, context: ContextTypes) -> None:
        new_content_text = update.message.text
        new_content_html = update.message.text_html if update.message.text_html else ""
        new_content_md = update.message.text_markdown if update.message.text_markdown else ""

        # create ticket
        ticket = {
            "action": "edit_annc",
            "ticket": {
                "creator_id": context.user_data["creator_id"],
                "creator_name": context.user_data["creator_name"],
                "old_ticket_id": context.user_data["old_ticket_id"],
                "new_content_text": new_content_text,
                "new_content_html": new_content_html,
                "new_content_md": new_content_md,
            },
        }
        res = self.client.create_ticket(**ticket)
        ticket_id = res["data"]["ticket_id"]
        message = self.get_confirm_message(ticket_id)

        keyboard = [
            [InlineKeyboardButton("Approve", callback_data=f"edit_approve_{ticket_id}")],
            [InlineKeyboardButton("Reject", callback_data=f"edit_reject_{ticket_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=self.CONFIRM_CHAT_ID if not self.is_test else self.TEST_CONFIRM_CHAT_ID,
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

        self.logger.info(
            f"Edit ticket `{ticket_id}` sent by {context.user_data['creator_name']}({context.user_data['creator_id']})"
        )

        message = (
            f"Your edit ticket has been sent to the admin group for approval, "
            f"please wait patiently\.\n"
            f"ID: `{ticket_id}`"
        )
        await update.message.reply_text(message, parse_mode="MarkdownV2")
        return ConversationHandler.END

    async def confirm_edit(self, update: Update, context: ContextTypes) -> None:
        operator = update.callback_query.from_user

        query = update.callback_query
        ticket_id = query.data.split("_")[-1]
        action = query.data.split("_")[1]

        if action == "approve":
            self.client.approve_ticket(ticket_id=ticket_id, user_id=str(operator.id))

        else:
            self.client.reject_ticket(ticket_id=ticket_id, user_id=str(operator.id))

        report_message = self.get_report_message(ticket_id)

        await query.message.edit_text(report_message, parse_mode="HTML")
        self.client.update_ticket_dashboard()

        self.logger.info(f"Edit ticket `{ticket_id}` ticket {action} by {operator.full_name}({operator.id})")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes) -> int:
        operator = update.message.from_user

        message = f"Bye {operator.full_name}! I hope we can talk again some day."

        await update.message.reply_text(message)
        return ConversationHandler.END

    def run(self) -> None:
        self.logger.info(f"Starting {self.name}...")
        app = Application.builder().token(self.command_bot_key).build()

        app.add_handler(CommandHandler("start", self.start))

        # post announcement pipeline
        post_handler = ConversationHandler(
            entry_points=[CommandHandler("post", self.post)],
            states={
                CATEGORY: [CallbackQueryHandler(self.choose_category, pattern=r"^category_.*")],
                LANGUAGE: [CallbackQueryHandler(self.choose_language, pattern="^(english|chinese)$")],
                LABEL: [MessageHandler(filters.TEXT, self.choose_label)],
                CONTENT: [
                    MessageHandler(
                        filters.TEXT & (~filters.COMMAND) | filters.PHOTO | filters.VIDEO, self.input_content
                    )
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_chat=False,
        )
        confirm_post_handler = CallbackQueryHandler(self.confirm_post, pattern="^(approve|reject)_.*")

        # edit announcement pipeline
        edit_handler = ConversationHandler(
            entry_points=[CommandHandler("edit", self.edit)],
            states={
                EDIT_TICKET_ID: [MessageHandler(filters.TEXT, self.choose_edit_ticket_id)],
                EDIT_NEW_CONTENT: [MessageHandler(filters.TEXT, self.input_edit_new_content)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
            per_chat=False,
        )
        confirm_edit_handler = CallbackQueryHandler(self.confirm_edit, pattern="^(edit_approve|edit_reject)_.*")

        # confirm post announcement pipeline
        app.add_handler(post_handler)
        app.add_handler(confirm_post_handler)
        app.add_handler(edit_handler)
        app.add_handler(confirm_edit_handler)
        app.run_polling()


if __name__ == "__main__":
    load_dotenv()
    args = init_args("CommandBot")
    bot = CommandBot(
        command_bot_key=os.getenv("COMMAND_BOT_TOKEN"),
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
        is_test=args.test,
    )

    bot.run()
