import pandas as pd
from fastapi import HTTPException

from app.chat_info.models import Chat, ChatInfoParams, DeleteChatInfo, UpdateChatInfo
from app.config.setting import settings as s
from app.db.dashboard import GCClient
from app.db.database import MongoClient

client = MongoClient(s.dev_db if s.is_test else s.prod_db)
collection = "chat_info"
gc_client = GCClient()


async def create_chat(chat: Chat):
    res = await client.find_one(collection, query={"chat_id": chat.chat_id})
    if res:
        raise HTTPException(status_code=400, detail=f"Chat already exists with id `{chat.chat_id}`")

    return await client.insert_one(collection, chat.model_dump())


async def get_chat_info(params: ChatInfoParams):
    """
    Query params have the following case:
    1. `chat_id`, `name` won't combine with other params
    2. `chat_type`, `language`, `category`, `label` can combine with `num`
        and logic will be `OR` between params and `AND` within each param
    """
    if params.chat_id:
        return [await client.find_one(collection, query={"chat_id": params.chat_id})]

    if params.name:
        return [await client.find_one(collection, query={"name": params.name})]

    query = {}
    if params.chat_type:
        query["chat_type"] = params.chat_type
    if params.language:
        query["language"] = {"$in": params.language}
    if params.category:
        query["category"] = {"$in": params.category}
    if params.label:
        query["label"] = {"$in": params.label}

    return await client.find_many(collection, query=query, limit=params.num)


async def update_chat_info(params: UpdateChatInfo):
    chat_data = await client.find_one(collection, query={"chat_id": params.chat_id})
    if not chat_data:
        raise HTTPException(status_code=400, detail=f"Chat not found with id `{params.chat_id}`")

    chat = Chat(**chat_data)
    chat.update(params)
    return await client.update_one(collection, query={"chat_id": params.chat_id}, update=chat.model_dump())


async def delete_chat(params: DeleteChatInfo):
    status = await client.delete_one(collection, query={"chat_id": params.chat_id})

    return {"delete_status": status}


async def update_chat_dashboard(direction: str = "pull", **kwargs):
    """
    This function will pull or push chat info to the google sheet,
    1. push is using when chat name, chat type, new chat created, deleted chat status changed
    2. pull is using whenever a user request to create a ticket, update the category, language, label on the dashboard to mongodb
    """
    fixed_columns_map = {
        "name": "Name",
        "chat_type": "Type",
        "created_timestamp": "Added Time",
        "label": "Label",
        "language": "Language",
        "category": "Category",
    }
    if direction == "push":
        ws = gc_client.get_ws(name="TG Chat Info", to_type="ws")
        chat_info = pd.DataFrame(await client.find_many(collection, query={"active": True}))[
            list(fixed_columns_map.keys())
        ].rename(columns=fixed_columns_map)

        chat_info["Label"] = chat_info["Label"].apply(lambda x: ", ".join(x) if x else "")
        chat_info["Language"] = chat_info["Language"].apply(lambda x: ", ".join(x) if x else "")

        unique_category = sorted(list(set([cat for cats in chat_info["Category"] for cat in cats])))

        for cat in unique_category:
            cat_title = cat.replace("_", " ").title()
            chat_info[cat_title] = chat_info["Category"].apply(lambda x: "V" if cat in x else "")
        chat_info.drop(columns=["Category"], inplace=True)
        chat_info["Added Time"] = pd.to_datetime(chat_info["Added Time"], unit="ms")

        # start writing to the google sheet
        ws.clear()
        ws.set_dataframe(chat_info, start="A1", copy_index=False, copy_head=True)

        return chat_info.to_dict(orient="records")
    elif direction == "pull":
        """
        Pull is using to update the online record to the mongo db.
        Category is the column between Description and Label
        """
        chat_info = gc_client.get_ws(name="TG Chat Info", to_type="df")  # .drop(columns=[""])
        category = list(chat_info.columns)[
            chat_info.columns.get_loc("Label") + 1 : chat_info.columns.get_loc("Description")
        ]

        chat_info["Category"] = chat_info.apply(
            lambda x: [cat.replace(" ", "_").lower() for cat in category if x[cat] == "V"], axis=1
        )
        chat_info["Label"] = chat_info["Label"].apply(lambda x: x.split(", ") if x else [])
        chat_info["Language"] = chat_info["Language"].apply(lambda x: x.split(", ") if x else [])

        reverse_columns_map = {v: k for k, v in fixed_columns_map.items()}
        chat_info = chat_info.rename(columns=reverse_columns_map)
        chat_info_db = await client.find_many(collection, query={"active": True})

        # combine the chat info from the google sheet and the mongo db
        results = []
        for data in chat_info_db:
            chat = Chat(**data)
            new_data = chat_info[chat_info["name"] == chat.name].to_dict(orient="records")[0]
            # dashboard can only update the category, language, label
            chat.update(
                UpdateChatInfo(
                    chat_id=chat.chat_id,
                    language=new_data["language"],
                    category=new_data["category"],
                    label=new_data["label"],
                )
            )

            results.append(
                await client.update_one(collection, query={"chat_id": chat.chat_id}, update=chat.model_dump())
            )
        return results
    else:
        raise HTTPException(status_code=400, detail=f"Invalid direction: {direction}. Only `pull` or `push` is allowed")
