from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from typing import Any, Optional, Dict, List
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
        return str(result.inserted_id)
    
    async def find_one(self, name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        collection: Collection = self.get_collection(name)
        result = await collection.find_one(query)
        return result

    async def find_many(self, name: str, query: Dict[str, Any], limit: int = 0, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        collection: Collection = self.get_collection(name)
        cursor = collection.find(query)

        if sort:
            cursor = cursor.sort(sort)

        if limit > 0:
            cursor = cursor.limit(limit)

        results = [i for i in cursor]  # Convert cursor to a list of documents
        return results

        async for document in cursor:
            document.pop('_id', None)
            result.append(document)
        return result
    
    async def update_one(self, name: str, query: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        collection: Collection = self.get_collection(name)
        result = await collection.find_one_and_update(
            query,
            {'$set': update},
            return_document=True
        )
        return result

    async def delete_one(self, name: str, query: Dict[str, Any]) -> bool:
        collection: Collection = self.get_collection(name)
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    async def close(self):
        self.client.close()