from functools import lru_cache
from typing import Any, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from analytics.infrastructure.configuration.config_service_client import ConfigServiceClient


class Settings(BaseSettings):
    service_name: str = "analytics-service"
    app_name: str = "Analytics Service"
    environment: str = "development"
    port: int = 8004
    api_prefix: str = "/api/v1/analytics"
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"])
    config_service_url: str = "http://localhost:8000"
    config_service_timeout_seconds: float = 3.0

    mongodb_uri: str = "mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority"
    mongodb_database: str = "sems_analytics_db"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "analytics-service-group"
    kafka_enabled: bool = True
    kafka_security_protocol: str = "PLAINTEXT"
    kafka_sasl_mechanism: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    kafka_consumed_topics: List[str] = Field(
        default_factory=lambda: [
            "energy.consumption.recorded",
            "device.registered",
            "device.updated",
        ]
    )
    kafka_topic_analytics_bill_prediction_generated: str = "analytics.bill_prediction.generated"
    kafka_topic_analytics_recommendation_generated: str = "analytics.recommendation.generated"
    kafka_topic_analytics_anomaly_detected: str = "analytics.anomaly.detected"
    kafka_topic_analytics_device_identified: str = "analytics.device_identified"
    kafka_topic_analytics_consumption_ranking_generated: str = "analytics.consumption_ranking.generated"

    default_tariff_per_kwh: float = 0.65
    default_currency: str = "USD"
    anomaly_threshold_percentage: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    base = Settings()
    if not base.config_service_url:
        return base

    client = ConfigServiceClient(base.config_service_url, timeout_seconds=base.config_service_timeout_seconds)
    remote = client.get_service_config(base.service_name)
    updates = _map_remote_to_settings(remote)
    return base.model_copy(update=updates)


def _map_remote_to_settings(remote: dict[str, Any]) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if not remote:
        return updates

    if isinstance(remote.get("apiPrefix"), str):
        updates["api_prefix"] = remote["apiPrefix"]
    elif isinstance(remote.get("routePrefix"), str):
        updates["api_prefix"] = remote["routePrefix"]

    kafka = remote.get("kafka")
    if isinstance(kafka, dict):
        _set_if_present(updates, "kafka_bootstrap_servers", kafka, ["bootstrapServers", "bootstrap_servers"])
        _set_if_present(updates, "kafka_consumer_group", kafka, ["consumerGroup", "consumer_group", "groupId"])
        _set_if_present(updates, "kafka_enabled", kafka, ["enabled", "kafkaEnabled"])
        _set_if_present(updates, "kafka_security_protocol", kafka, ["securityProtocol", "security_protocol"])
        _set_if_present(updates, "kafka_sasl_mechanism", kafka, ["saslMechanism", "sasl_mechanism"])
        _set_if_present(updates, "kafka_consumed_topics", kafka, ["consumedTopics", "topicsConsume", "topics_consume"])

        produced = kafka.get("producedTopics") or kafka.get("topicsProduce") or kafka.get("topics_produce")
        if isinstance(produced, dict):
            _set_if_present(
                updates,
                "kafka_topic_analytics_bill_prediction_generated",
                produced,
                ["billPredictionGenerated", "analytics.bill_prediction.generated"],
            )
            _set_if_present(
                updates,
                "kafka_topic_analytics_recommendation_generated",
                produced,
                ["recommendationGenerated", "analytics.recommendation.generated"],
            )
            _set_if_present(
                updates,
                "kafka_topic_analytics_anomaly_detected",
                produced,
                ["anomalyDetected", "analytics.anomaly.detected"],
            )
            _set_if_present(
                updates,
                "kafka_topic_analytics_device_identified",
                produced,
                ["deviceIdentified", "analytics.device_identified"],
            )
            _set_if_present(
                updates,
                "kafka_topic_analytics_consumption_ranking_generated",
                produced,
                ["consumptionRankingGenerated", "analytics.consumption_ranking.generated"],
            )

    business = remote.get("businessRules") if isinstance(remote.get("businessRules"), dict) else remote
    _set_if_present(updates, "default_tariff_per_kwh", business, ["defaultTariffPerKwh", "default_tariff_per_kwh"])
    _set_if_present(updates, "default_currency", business, ["defaultCurrency", "default_currency"])
    _set_if_present(
        updates,
        "anomaly_threshold_percentage",
        business,
        ["anomalyThresholdPercentage", "anomaly_threshold_percentage"],
    )

    cors = remote.get("cors")
    if isinstance(cors, dict):
        _set_if_present(updates, "allowed_origins", cors, ["allowedOrigins", "allowed_origins"])

    return updates


def _set_if_present(target: dict[str, Any], target_key: str, source: dict[str, Any], source_keys: list[str]) -> None:
    for source_key in source_keys:
        value = source.get(source_key)
        if value is not None:
            target[target_key] = value
            return
