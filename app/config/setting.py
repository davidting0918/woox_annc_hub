from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_db_url: str
    prod_db: str
    dev_db: str
    is_test: bool = False

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
