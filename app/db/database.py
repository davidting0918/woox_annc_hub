from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection

from app.config.setting import settings


class MongoClient:
    def __init__(self, db: str):
        self.client = AsyncIOMotorClient(settings.mongo_db_url)
        self.db = self.client[db]

    def get_collection(self, name: str) -> Collection:
        return self.db[name]

    async def insert_one(self, name: str, document: dict) -> str:
        collection = self.get_collection(name)
        result = await collection.insert_one(document)
        if str(result.inserted_id):
            return await self.find_one(name, {"_id": result.inserted_id})

    async def insert_many(self, name: str, documents: List[dict]) -> List[str]:
        collection = self.get_collection(name)
        result = await collection.insert_many(documents)
        return await self.find_many(name, {"_id": {"$in": result.inserted_ids}})

    async def find_one(self, name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        collection: Collection = self.get_collection(name)
        result = await collection.find_one(query)
        if result:
            result.pop("_id", None)
        return result

    async def find_many(
        self, name: str, query: Dict[str, Any], limit: int = 0, sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        collection: Collection = self.get_collection(name)
        cursor = collection.find(query)

        if sort:
            cursor = cursor.sort(sort)

        if limit > 0:
            cursor = cursor.limit(limit)

        result = []
        async for document in cursor:
            document.pop("_id", None)
            result.append(document)
        return result

    async def update_one(self, name: str, query: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        collection: Collection = self.get_collection(name)
        result = await collection.find_one_and_update(query, {"$set": update}, return_document=True)
        result.pop("_id", None)
        return result

    async def delete_one(self, name: str, query: Dict[str, Any]) -> bool:
        collection: Collection = self.get_collection(name)
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    async def delete_many(self, name: str, query: Dict[str, Any]) -> bool:
        collection: Collection = self.get_collection(name)
        result = await collection.delete_many(query)
        return result.deleted_count > 0

    async def close(self):
        self.client.close()
