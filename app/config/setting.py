import os
from dotenv import load_dotenv
class Settings:
    def __init__(self):
        load_dotenv()
        self.mongo_db_url: str = os.getenv("MONGO_DB_URL")
        self.db_name: str = os.getenv("DB_NAME")


settings = Settings()