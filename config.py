import logging.config
from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):
    USER_NAME: str
    PASSWORD: str
    IP_ADDR: str
    PORT: str
    DB_NAME: str

    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_TIMEOUT: int

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )


class Settings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    
    # 보안 설정
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='allow'
    )

    def get_database_url(self, driver: Literal["postgresql"]) -> str:
        return (
            f'{driver}://{self.db.USER_NAME}:{quote_plus(self.db.PASSWORD)}'
            f'@{self.db.IP_ADDR}:{self.db.PORT}/{self.db.DB_NAME}'
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.get_database_url('postgresql')


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    return settings
