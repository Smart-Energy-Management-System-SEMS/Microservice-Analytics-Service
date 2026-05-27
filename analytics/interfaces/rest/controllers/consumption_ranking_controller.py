from fastapi import APIRouter, Depends

from analytics.application.commandservices.consumption_ranking_command_service import ConsumptionRankingCommandService
from analytics.application.queryservices.consumption_ranking_query_service import ConsumptionRankingQueryService
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.interfaces.rest.controllers.dependencies import (
    get_consumption_ranking_command_service,
    get_consumption_ranking_query_service,
)
from analytics.interfaces.rest.resources.consumption_ranking_resource import (
    ConsumptionRankingResponse,
    CreateConsumptionRankingRequest,
)
from analytics.interfaces.rest.transform import consumption_ranking_transform as transform

router = APIRouter(prefix="/consumption-rankings", tags=["Consumption Rankings"])


@router.get("/user/{user_id}", response_model=list[ConsumptionRankingResponse])
async def get_consumption_rankings_by_user(
    user_id: str,
    query_service: ConsumptionRankingQueryService = Depends(get_consumption_ranking_query_service),
) -> list[ConsumptionRankingResponse]:
    rankings = await query_service.get_by_user(GetByUserQuery(user_id=user_id))
    return [transform.entity_to_response(ranking) for ranking in rankings]


@router.post("", response_model=ConsumptionRankingResponse, status_code=201)
async def create_consumption_ranking(
    request: CreateConsumptionRankingRequest,
    command_service: ConsumptionRankingCommandService = Depends(get_consumption_ranking_command_service),
) -> ConsumptionRankingResponse:
    ranking = await command_service.create(transform.request_to_command(request))
    return transform.entity_to_response(ranking)
