from analytics.infrastructure.configuration.settings import get_settings

settings = get_settings()

CONSUMED_TOPICS = tuple(settings.kafka_consumed_topics)
ENERGY_EVENTS_TOPIC = settings.kafka_topic_energy_events
ANALYTICS_EVENTS_TOPIC = settings.kafka_topic_analytics_events

ENERGY_CONSUMPTION_RECORDED = settings.kafka_event_type_energy_consumption_recorded
SUPPORTED_CONSUMED_EVENT_TYPES = frozenset(
    [
        ENERGY_CONSUMPTION_RECORDED,
    ]
)
CONSUMED_EVENT_TYPES = frozenset(
    event_type for event_type in settings.kafka_consumed_event_types if event_type in SUPPORTED_CONSUMED_EVENT_TYPES
) or SUPPORTED_CONSUMED_EVENT_TYPES

ANALYTICS_BILL_PREDICTION_GENERATED = settings.kafka_event_type_analytics_bill_prediction_generated
ANALYTICS_RECOMMENDATION_GENERATED = settings.kafka_event_type_analytics_recommendation_generated
ANALYTICS_ANOMALY_DETECTED = settings.kafka_event_type_analytics_anomaly_detected
ANALYTICS_DEVICE_IDENTIFIED = settings.kafka_event_type_analytics_device_identified
ANALYTICS_CONSUMPTION_RANKING_GENERATED = settings.kafka_event_type_analytics_consumption_ranking_generated
