from analytics.domain.model.commands.create_consumption_ranking_command import (
    CreateConsumptionRankingCommand,
    RankingSourceItem,
)
from analytics.domain.model.entities.consumption_ranking import ConsumptionRanking
from analytics.interfaces.rest.resources.consumption_ranking_resource import (
    ConsumptionRankingResponse,
    CreateConsumptionRankingRequest,
    RankingItemResponse,
)


def request_to_command(request: CreateConsumptionRankingRequest) -> CreateConsumptionRankingCommand:
    data = request.model_dump()
    devices = [RankingSourceItem(**item) for item in data.pop("devices")]
    return CreateConsumptionRankingCommand(devices=devices, **data)


def entity_to_response(entity: ConsumptionRanking) -> ConsumptionRankingResponse:
    return ConsumptionRankingResponse(
        id=entity.id or "",
        user_id=entity.user_id,
        period_type=entity.period_type,
        period_start=entity.period_start,
        period_end=entity.period_end,
        rankings=[RankingItemResponse(**item.__dict__) for item in entity.rankings],
        generated_at=entity.generated_at,
        created_at=entity.created_at,
    )
