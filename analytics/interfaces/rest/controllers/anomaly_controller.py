from fastapi import APIRouter, Depends, HTTPException

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.queryservices.anomaly_query_service import AnomalyQueryService
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.interfaces.rest.controllers.dependencies import get_anomaly_command_service, get_anomaly_query_service
from analytics.interfaces.rest.resources.anomaly_resource import AnomalyResponse, CreateAnomalyRequest
from analytics.interfaces.rest.transform import anomaly_transform as transform

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("/user/{user_id}", response_model=list[AnomalyResponse])
async def get_anomalies_by_user(
    user_id: str,
    query_service: AnomalyQueryService = Depends(get_anomaly_query_service),
) -> list[AnomalyResponse]:
    anomalies = await query_service.get_by_user(GetByUserQuery(user_id=user_id))
    return [transform.entity_to_response(anomaly) for anomaly in anomalies]


@router.post("", response_model=AnomalyResponse, status_code=201)
async def create_anomaly(
    request: CreateAnomalyRequest,
    command_service: AnomalyCommandService = Depends(get_anomaly_command_service),
) -> AnomalyResponse:
    anomaly = await command_service.create(transform.request_to_command(request))
    return transform.entity_to_response(anomaly)


@router.patch("/{anomaly_id}/resolve", response_model=AnomalyResponse)
async def resolve_anomaly(
    anomaly_id: str,
    command_service: AnomalyCommandService = Depends(get_anomaly_command_service),
) -> AnomalyResponse:
    anomaly = await command_service.resolve(anomaly_id)
    if anomaly is None:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return transform.entity_to_response(anomaly)
