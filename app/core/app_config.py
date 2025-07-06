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

    # OpenTelemetry settings
    enable_otel: bool = Field(default=False, alias="ENABLE_OTEL")
    otel_exporter: str = Field(default="console", alias="OTEL_EXPORTER")
    otel_service_name: str = Field(
        default="blood-donation-api", alias="OTEL_SERVICE_NAME"
    )
    otel_exporter_otlp_endpoint: str = Field(
        default="", alias="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    otel_sample_rate: float = Field(1.0, alias="OTEL_SAMPLE_RATE")  # 1.0 = 100%


app_settings = AppSettings()  # type: ignore
