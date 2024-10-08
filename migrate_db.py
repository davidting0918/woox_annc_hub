import asyncio
from datetime import datetime as dt

import pandas as pd

from app.config.setting import settings
from app.db.database import MongoClient

new_db_client = MongoClient(settings.prod_db)
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

    # first clear the new table
    await new_db_client.delete_many(new_table, query={})
    res = await new_db_client.insert_many(new_table, datas)

    return res


async def migrate_chats():
    old_table = "ChatInfo"
    new_table = "chat_info"
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
                "test_channel",
            ]
            if data[i]
        ]
        data["category"] = category

        language = [i for i in data["label"] if i in language_list]
        data["language"] = language

        label = [i for i in data["label"] if i not in language_list]
        data["label"] = label

        data["active"] = True

        # convert timestamp
        data["created_timestamp"] = (
            int(
                dt.strptime(
                    data["created_timestamp"],
                    "%Y-%m-%d" if len(data["created_timestamp"]) == 10 else "%Y-%m-%d %H:%M:%S",
                ).timestamp()
            )
            * 1000
        )
        data["updated_timestamp"] = (
            int(
                dt.strptime(
                    data["updated_timestamp"],
                    "%Y-%m-%d" if len(data["updated_timestamp"]) == 10 else "%Y-%m-%d %H:%M:%S",
                ).timestamp()
            )
            * 1000
            if data["updated_timestamp"]
            else data["created_timestamp"]
        )
        continue

    df = pd.DataFrame(datas)

    to_columns = [
        "chat_id",
        "name",
        "chat_type",
        "language",
        "category",
        "label",
        "active",
        "created_timestamp",
        "updated_timestamp",
        "description",
    ]
    chats_df = df[to_columns].to_dict(orient="records")

    # first clear the new table
    await new_db_client.delete_many(new_table, query={})
    res = await new_db_client.insert_many(new_table, chats_df)

    return res


async def main():
    output = await asyncio.gather(migrate_users(), migrate_chats())
    return output


if __name__ == "__main__":
    print("Migrating data from old database to new database")
    asyncio.run(main())
