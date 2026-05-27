from fastapi import APIRouter, Depends, HTTPException

from analytics.application.commandservices.recommendation_command_service import RecommendationCommandService
from analytics.application.queryservices.recommendation_query_service import RecommendationQueryService
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.interfaces.rest.controllers.dependencies import (
    get_recommendation_command_service,
    get_recommendation_query_service,
)
from analytics.interfaces.rest.resources.recommendation_resource import CreateRecommendationRequest, RecommendationResponse
from analytics.interfaces.rest.transform import recommendation_transform as transform

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/user/{user_id}", response_model=list[RecommendationResponse])
async def get_recommendations_by_user(
    user_id: str,
    query_service: RecommendationQueryService = Depends(get_recommendation_query_service),
) -> list[RecommendationResponse]:
    recommendations = await query_service.get_by_user(GetByUserQuery(user_id=user_id))
    return [transform.entity_to_response(recommendation) for recommendation in recommendations]


@router.post("", response_model=RecommendationResponse, status_code=201)
async def create_recommendation(
    request: CreateRecommendationRequest,
    command_service: RecommendationCommandService = Depends(get_recommendation_command_service),
) -> RecommendationResponse:
    recommendation = await command_service.create(transform.request_to_command(request))
    return transform.entity_to_response(recommendation)


@router.patch("/{recommendation_id}/apply", response_model=RecommendationResponse)
async def apply_recommendation(
    recommendation_id: str,
    command_service: RecommendationCommandService = Depends(get_recommendation_command_service),
) -> RecommendationResponse:
    recommendation = await command_service.apply(recommendation_id)
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return transform.entity_to_response(recommendation)
