import logging
from contextlib import asynccontextmanager

from aiokafka.errors import KafkaError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.bill_prediction_command_service import BillPredictionCommandService
from analytics.application.commandservices.consumption_ranking_command_service import ConsumptionRankingCommandService
from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.application.commandservices.recommendation_command_service import RecommendationCommandService
from analytics.application.eventhandlers.analytics_event_handler import AnalyticsEventHandler
from analytics.application.outboundservices.analytics_event_publisher import AnalyticsEventPublisher
from analytics.application.queryservices.anomaly_query_service import AnomalyQueryService
from analytics.application.queryservices.bill_prediction_query_service import BillPredictionQueryService
from analytics.application.queryservices.consumption_ranking_query_service import ConsumptionRankingQueryService
from analytics.application.queryservices.device_identification_query_service import DeviceIdentificationQueryService
from analytics.application.queryservices.recommendation_query_service import RecommendationQueryService
from analytics.domain.services.analytics_rule_service import AnalyticsRuleService
from analytics.infrastructure.configuration.settings import get_settings
from analytics.infrastructure.messaging.kafka.kafka_consumer import KafkaConsumerAdapter
from analytics.infrastructure.messaging.kafka.kafka_producer import KafkaProducerAdapter
from analytics.infrastructure.persistence.mongodb.configuration.mongodb_client import MongoDBClient
from analytics.infrastructure.persistence.mongodb.repositories.anomaly_mongodb_repository import AnomalyMongoDBRepository
from analytics.infrastructure.persistence.mongodb.repositories.bill_prediction_mongodb_repository import (
    BillPredictionMongoDBRepository,
)
from analytics.infrastructure.persistence.mongodb.repositories.consumption_ranking_mongodb_repository import (
    ConsumptionRankingMongoDBRepository,
)
from analytics.infrastructure.persistence.mongodb.repositories.device_identification_result_mongodb_repository import (
    DeviceIdentificationResultMongoDBRepository,
)
from analytics.infrastructure.persistence.mongodb.repositories.recommendation_mongodb_repository import (
    RecommendationMongoDBRepository,
)
from analytics.interfaces.rest.controllers import (
    anomaly_controller,
    bill_prediction_controller,
    consumption_ranking_controller,
    device_identification_controller,
    health_controller,
    recommendation_controller,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    mongodb_client = MongoDBClient(settings)
    await mongodb_client.connect()
    database = mongodb_client.database

    rule_service = AnalyticsRuleService()
    producer: KafkaProducerAdapter | None = None
    consumer: KafkaConsumerAdapter | None = None

    if settings.kafka_enabled:
        producer_candidate = KafkaProducerAdapter(settings.kafka_bootstrap_servers)
        try:
            await producer_candidate.start()
            producer = producer_candidate
        except KafkaError:
            logger.exception("Kafka producer could not start; publishing will be disabled")
            producer = None

    event_publisher = AnalyticsEventPublisher(producer)

    device_repository = DeviceIdentificationResultMongoDBRepository(database)
    bill_repository = BillPredictionMongoDBRepository(database)
    recommendation_repository = RecommendationMongoDBRepository(database)
    anomaly_repository = AnomalyMongoDBRepository(database)
    ranking_repository = ConsumptionRankingMongoDBRepository(database)

    fastapi_app.state.device_identification_command_service = DeviceIdentificationCommandService(
        device_repository,
        rule_service,
        event_publisher,
    )
    fastapi_app.state.device_identification_query_service = DeviceIdentificationQueryService(device_repository)
    fastapi_app.state.bill_prediction_command_service = BillPredictionCommandService(
        bill_repository,
        rule_service,
        event_publisher,
    )
    fastapi_app.state.bill_prediction_query_service = BillPredictionQueryService(bill_repository)
    fastapi_app.state.recommendation_command_service = RecommendationCommandService(
        recommendation_repository,
        rule_service,
        event_publisher,
    )
    fastapi_app.state.recommendation_query_service = RecommendationQueryService(recommendation_repository)
    fastapi_app.state.anomaly_command_service = AnomalyCommandService(
        anomaly_repository,
        rule_service,
        event_publisher,
    )
    fastapi_app.state.anomaly_query_service = AnomalyQueryService(anomaly_repository)
    fastapi_app.state.consumption_ranking_command_service = ConsumptionRankingCommandService(
        ranking_repository,
        rule_service,
        event_publisher,
    )
    fastapi_app.state.consumption_ranking_query_service = ConsumptionRankingQueryService(ranking_repository)

    if settings.kafka_enabled:
        event_handler = AnalyticsEventHandler(
            fastapi_app.state.device_identification_command_service,
            fastapi_app.state.anomaly_command_service,
        )
        consumer_candidate = KafkaConsumerAdapter(
            settings.kafka_bootstrap_servers,
            settings.kafka_consumer_group,
            event_handler.handle,
        )
        try:
            await consumer_candidate.start()
            consumer = consumer_candidate
        except KafkaError:
            logger.exception("Kafka consumer could not start; consuming will be disabled")
            consumer = None

    try:
        yield
    finally:
        if consumer is not None:
            await consumer.stop()
        if producer is not None:
            await producer.stop()
        await mongodb_client.close()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Analytics Service for Smart Energy Management System",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1/analytics"
app.include_router(health_controller.router, prefix=API_PREFIX)
app.include_router(device_identification_controller.router, prefix=API_PREFIX)
app.include_router(bill_prediction_controller.router, prefix=API_PREFIX)
app.include_router(recommendation_controller.router, prefix=API_PREFIX)
app.include_router(anomaly_controller.router, prefix=API_PREFIX)
app.include_router(consumption_ranking_controller.router, prefix=API_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
