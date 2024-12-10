from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_TIMEOUT: int

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()

    # 보안 설정
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="allow"
    )

    def get_database_url(self, driver: Literal["postgresql"]) -> str:
        return (
            f"{driver}://{self.db.DB_USER}:{quote_plus(self.db.DB_PASSWORD)}"
            f"@{self.db.DB_HOST}:{self.db.DB_PORT}/{self.db.DB_NAME}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.get_database_url("postgresql")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    return settings
