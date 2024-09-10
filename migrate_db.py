import asyncio
from datetime import datetime as dt

import pandas as pd

from app.config.setting import settings
from app.db.database import MongoClient

new_db_client = MongoClient(settings.db_name)
old_db_client = MongoClient("AnnouncementDB")


async def migrate_users():
    old_table = "Permissions"
    new_table = "permission"
    users = await old_db_client.find_many(old_table, query={})

    # key is the old key and value is the new key
    key_dict = {
        "id": "user_id",
        "name": "name",
        "admin": "admin",
        "whitelist": "whitelist",
        "update_time": "updated_timestamp",
    }
    df = pd.DataFrame(users)

    df.rename(columns=key_dict, inplace=True)
    df["updated_timestamp"].fillna("2023-11-23 16:56:17", inplace=True)
    df["updated_timestamp"] = df["updated_timestamp"].apply(
        lambda x: int(dt.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp()) * 1000
    )
    df["created_timestamp"] = df["updated_timestamp"]

    datas = df.to_dict(orient="records")
    for data in datas:
        await new_db_client.insert_one(new_table, data)

    return


async def migrate_chats():
    old_table = "ChatInfo"
    # new_table = "chat_info"
    chat_info = await old_db_client.find_many(old_table, query={})

    # key is the old key and value is the new key
    key_dict = {
        "id": "chat_id",
        "name": "name",
        "type": "chat_type",
        "label": "label",
        "description": "description",
        "operator_id": "operator_id",
        "add_time": "created_timestamp",
        "update_time": "updated_timestamp",
    }

    df = pd.DataFrame(chat_info).rename(columns=key_dict)
    datas = df.to_dict(orient="records")

    # add category, language, status fields and also change the timestamp format
    language_list = ["english", "chinese"]
    for data in datas:
        category = [
            i
            for i in [
                "maintenance",
                "listing",
                "delisting",
                "trading_suspension_resumption",
                "funding_rate",
                "dmm_program",
                "vip_program",
                "new_trading_competition",
            ]
            if data[i]
        ]
        data["category"] = category

        language = [i for i in data["label"] if i in language_list]
        data["language"] = language

        label = [i for i in data["label"] if i not in language_list]
        data["label"] = label

        data["active"] = True
        continue

    df = pd.DataFrame(datas)

    return df


if __name__ == "__main__":
    print("Migrating data from old database to new database")

    asyncio.run(migrate_users())
    asyncio.run(migrate_chats())
