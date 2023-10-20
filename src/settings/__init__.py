from pydantic_settings import SettingsConfigDict

from src.settings.application import AppSettings
from src.settings.celery import CelerySettings
from src.settings.database import DatabaseSettings
from src.settings.email import EmailSettings
from src.settings.jwt import JWTSettings


class Settings(
    AppSettings,
    CelerySettings,
    JWTSettings,
    EmailSettings,
    DatabaseSettings,
):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()  # type: ignore
