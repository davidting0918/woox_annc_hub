from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_db_url: str
    db_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
