from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Analytics Service"
    environment: str = "development"
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])

    mongodb_uri: str = "mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority"
    mongodb_database: str = "sems_analytics_db"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "analytics-service-group"
    kafka_enabled: bool = True

    default_tariff_per_kwh: float = 0.65
    default_currency: str = "USD"
    anomaly_threshold_percentage: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
