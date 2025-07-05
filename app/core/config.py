import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        # populate_by_name = True
    )

    app_env: str = Field(default="local", alias="APP_ENV")
    database_url: str = Field(..., alias="DATABASE_URL")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    api_prefix: str = Field(default="/api/v1", alias="PREFIX")


app_settings = AppSettings()  # type: ignore
