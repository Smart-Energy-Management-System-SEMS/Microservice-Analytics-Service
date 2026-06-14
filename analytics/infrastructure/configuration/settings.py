import json
from functools import lru_cache
from typing import Annotated, Any, List

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

from analytics.infrastructure.configuration.config_service_client import ConfigServiceClient


class Settings(BaseSettings):
    service_name: str = "analytics-service"
    app_name: str = "Analytics Service"
    environment: str = "development"
    port: int = Field(default=8004, validation_alias=AliasChoices("PORT"))
    api_prefix: str = "/api/v1/analytics"
    allowed_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        validation_alias=AliasChoices("ALLOWED_ORIGINS"),
    )
    config_service_url: str = Field(
        default="http://config-service:8090",
        validation_alias=AliasChoices("CONFIG_SERVICE_URL"),
    )
    config_service_timeout_seconds: float = 3.0

    mongodb_uri: str = Field(
        default="mongodb+srv://<user>:<password>@<cluster>/<database>?retryWrites=true&w=majority",
        validation_alias=AliasChoices("MONGODB_URI", "DATABASE_URL"),
    )
    mongodb_database: str = "sems_analytics_db"

    kafka_bootstrap_servers: str = Field(
        default="kafka:9092",
        validation_alias=AliasChoices("KAFKA_BROKERS", "KAFKA_BOOTSTRAP_SERVERS"),
    )
    kafka_consumer_group: str = "analytics-service-group"
    kafka_enabled: bool = True
    kafka_security_protocol: str = Field(
        default="PLAINTEXT",
        validation_alias=AliasChoices("KAFKA_SECURITY_PROTOCOL"),
    )
    kafka_sasl_mechanism: str = Field(
        default="",
        validation_alias=AliasChoices("KAFKA_SASL_MECHANISM"),
    )
    kafka_sasl_username: str = Field(
        default="",
        validation_alias=AliasChoices("KAFKA_USERNAME", "KAFKA_SASL_USERNAME"),
    )
    kafka_sasl_password: str = Field(
        default="",
        validation_alias=AliasChoices("KAFKA_PASSWORD", "KAFKA_SASL_PASSWORD"),
    )
    kafka_topic_energy_events: str = Field(
        default="energy.events",
        validation_alias=AliasChoices("KAFKA_TOPIC_ENERGY_EVENTS"),
    )
    kafka_topic_analytics_events: str = Field(
        default="analytics.events",
        validation_alias=AliasChoices("KAFKA_TOPIC_ANALYTICS_EVENTS"),
    )
    kafka_consumed_topics: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("KAFKA_CONSUMED_TOPICS"),
    )
    kafka_consumed_event_types: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("KAFKA_CONSUMED_EVENT_TYPES"),
    )
    kafka_event_type_energy_consumption_recorded: str = Field(
        default="energy.consumption.recorded",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ENERGY_CONSUMPTION_RECORDED"),
    )
    kafka_event_type_energy_reading_created: str = Field(
        default="energy.reading.created",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ENERGY_READING_CREATED"),
    )
    kafka_event_type_analytics_bill_prediction_generated: str = Field(
        default="analytics.bill_prediction.generated",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ANALYTICS_BILL_PREDICTION_GENERATED"),
    )
    kafka_event_type_analytics_recommendation_generated: str = Field(
        default="analytics.recommendation.generated",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ANALYTICS_RECOMMENDATION_GENERATED"),
    )
    kafka_event_type_analytics_anomaly_detected: str = Field(
        default="analytics.anomaly.detected",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ANALYTICS_ANOMALY_DETECTED"),
    )
    kafka_event_type_analytics_device_identified: str = Field(
        default="analytics.device_identified",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ANALYTICS_DEVICE_IDENTIFIED"),
    )
    kafka_event_type_analytics_consumption_ranking_generated: str = Field(
        default="analytics.consumption_ranking.generated",
        validation_alias=AliasChoices("KAFKA_EVENT_TYPE_ANALYTICS_CONSUMPTION_RANKING_GENERATED"),
    )
    azure_event_hubs_fqdn: str = Field(
        default="",
        validation_alias=AliasChoices("AZURE_EVENT_HUBS_FQDN"),
    )
    azure_event_hubs_username: str = Field(
        default="$ConnectionString",
        validation_alias=AliasChoices("AZURE_EVENT_HUBS_USERNAME"),
    )
    azure_event_hubs_connection_string: str = Field(
        default="",
        validation_alias=AliasChoices("AZURE_EVENT_HUBS_CONNECTION_STRING"),
    )

    default_tariff_per_kwh: float = 0.65
    default_currency: str = "USD"
    anomaly_threshold_percentage: float = 30.0

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return ["http://localhost:3000", "http://localhost:5173"]
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed if str(origin).strip()]
                return ["http://localhost:3000", "http://localhost:5173"]
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return value

    @field_validator("kafka_consumed_topics", "kafka_consumed_event_types", mode="before")
    @classmethod
    def _parse_string_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
                return []
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    def model_post_init(self, __context: Any) -> None:
        if self.azure_event_hubs_fqdn:
            if not self.kafka_bootstrap_servers or self.kafka_bootstrap_servers == "kafka:9092":
                self.kafka_bootstrap_servers = f"{self.azure_event_hubs_fqdn}:9093"
            if not self.kafka_security_protocol or self.kafka_security_protocol == "PLAINTEXT":
                self.kafka_security_protocol = "SASL_SSL"
            if not self.kafka_sasl_mechanism:
                self.kafka_sasl_mechanism = "PLAIN"
            if not self.kafka_sasl_username:
                self.kafka_sasl_username = self.azure_event_hubs_username
            if not self.kafka_sasl_password and self.azure_event_hubs_connection_string:
                self.kafka_sasl_password = self.azure_event_hubs_connection_string
        if not self.kafka_consumed_topics:
            self.kafka_consumed_topics = _default_consumed_topics(self)
        self.kafka_consumed_topics = _normalize_unique(self.kafka_consumed_topics)
        if not self.kafka_consumed_event_types:
            self.kafka_consumed_event_types = _default_consumed_event_types(self)
        self.kafka_consumed_event_types = _normalize_unique(self.kafka_consumed_event_types)


@lru_cache
def get_settings() -> Settings:
    base = Settings()
    if not base.config_service_url:
        return base

    client = ConfigServiceClient(base.config_service_url, timeout_seconds=base.config_service_timeout_seconds)
    remote = client.get_service_config(base.service_name)
    updates = _map_remote_to_settings(remote)
    resolved = base.model_copy(update=updates)
    if "kafka_consumed_topics" not in updates:
        resolved.kafka_consumed_topics = _default_consumed_topics(resolved)
    resolved.kafka_consumed_topics = _normalize_unique(resolved.kafka_consumed_topics)
    if "kafka_consumed_event_types" not in updates:
        resolved.kafka_consumed_event_types = _default_consumed_event_types(resolved)
    resolved.kafka_consumed_event_types = _normalize_unique(resolved.kafka_consumed_event_types)
    return resolved


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
        _set_if_present(
            updates,
            "kafka_consumed_event_types",
            kafka,
            ["consumedEventTypes", "eventTypesConsume", "event_types_consume"],
        )
        _set_if_present(updates, "kafka_topic_energy_events", kafka, ["energyEvents", "energy.events"])
        _set_if_present(updates, "kafka_topic_analytics_events", kafka, ["analyticsEvents", "analytics.events"])
        _set_if_present(
            updates,
            "kafka_event_type_energy_consumption_recorded",
            kafka,
            ["energyConsumptionRecorded", "energy.consumption.recorded"],
        )
        _set_if_present(
            updates,
            "kafka_event_type_energy_reading_created",
            kafka,
            ["energyReadingCreated", "energy.reading.created"],
        )
        _set_if_present(updates, "azure_event_hubs_fqdn", kafka, ["azureEventHubsFqdn", "eventHubsFqdn"])
        _set_if_present(
            updates,
            "azure_event_hubs_username",
            kafka,
            ["azureEventHubsUsername", "eventHubsUsername"],
        )
        _set_if_present(
            updates,
            "azure_event_hubs_connection_string",
            kafka,
            ["azureEventHubsConnectionString", "eventHubsConnectionString"],
        )

        produced = kafka.get("producedTopics") or kafka.get("topicsProduce") or kafka.get("topics_produce")
        if isinstance(produced, dict):
            _set_if_present(
                updates,
                "kafka_event_type_analytics_bill_prediction_generated",
                produced,
                ["billPredictionGenerated", "analytics.bill_prediction.generated"],
            )
            _set_if_present(
                updates,
                "kafka_event_type_analytics_recommendation_generated",
                produced,
                ["recommendationGenerated", "analytics.recommendation.generated"],
            )
            _set_if_present(
                updates,
                "kafka_event_type_analytics_anomaly_detected",
                produced,
                ["anomalyDetected", "analytics.anomaly.detected"],
            )
            _set_if_present(
                updates,
                "kafka_event_type_analytics_device_identified",
                produced,
                ["deviceIdentified", "analytics.device_identified"],
            )
            _set_if_present(
                updates,
                "kafka_event_type_analytics_consumption_ranking_generated",
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


def _default_consumed_topics(settings: Settings) -> list[str]:
    return [settings.kafka_topic_energy_events]


def _default_consumed_event_types(settings: Settings) -> list[str]:
    return [
        settings.kafka_event_type_energy_reading_created,
    ]


def _normalize_unique(items: list[str]) -> list[str]:
    normalized: list[str] = []
    for item in items:
        if item and item not in normalized:
            normalized.append(item)
    return normalized
