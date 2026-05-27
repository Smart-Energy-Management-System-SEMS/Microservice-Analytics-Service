from fastapi import Request

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.bill_prediction_command_service import BillPredictionCommandService
from analytics.application.commandservices.consumption_ranking_command_service import ConsumptionRankingCommandService
from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.application.commandservices.recommendation_command_service import RecommendationCommandService
from analytics.application.queryservices.anomaly_query_service import AnomalyQueryService
from analytics.application.queryservices.bill_prediction_query_service import BillPredictionQueryService
from analytics.application.queryservices.consumption_ranking_query_service import ConsumptionRankingQueryService
from analytics.application.queryservices.device_identification_query_service import DeviceIdentificationQueryService
from analytics.application.queryservices.recommendation_query_service import RecommendationQueryService


def get_device_identification_command_service(request: Request) -> DeviceIdentificationCommandService:
    return request.app.state.device_identification_command_service


def get_device_identification_query_service(request: Request) -> DeviceIdentificationQueryService:
    return request.app.state.device_identification_query_service


def get_bill_prediction_command_service(request: Request) -> BillPredictionCommandService:
    return request.app.state.bill_prediction_command_service


def get_bill_prediction_query_service(request: Request) -> BillPredictionQueryService:
    return request.app.state.bill_prediction_query_service


def get_recommendation_command_service(request: Request) -> RecommendationCommandService:
    return request.app.state.recommendation_command_service


def get_recommendation_query_service(request: Request) -> RecommendationQueryService:
    return request.app.state.recommendation_query_service


def get_anomaly_command_service(request: Request) -> AnomalyCommandService:
    return request.app.state.anomaly_command_service


def get_anomaly_query_service(request: Request) -> AnomalyQueryService:
    return request.app.state.anomaly_query_service


def get_consumption_ranking_command_service(request: Request) -> ConsumptionRankingCommandService:
    return request.app.state.consumption_ranking_command_service


def get_consumption_ranking_query_service(request: Request) -> ConsumptionRankingQueryService:
    return request.app.state.consumption_ranking_query_service
