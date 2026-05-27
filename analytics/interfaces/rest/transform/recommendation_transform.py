from dataclasses import asdict

from analytics.domain.model.commands.create_recommendation_command import CreateRecommendationCommand
from analytics.domain.model.entities.recommendation import Recommendation
from analytics.interfaces.rest.resources.recommendation_resource import CreateRecommendationRequest, RecommendationResponse


def request_to_command(request: CreateRecommendationRequest) -> CreateRecommendationCommand:
    return CreateRecommendationCommand(**request.model_dump())


def entity_to_response(entity: Recommendation) -> RecommendationResponse:
    return RecommendationResponse(**asdict(entity))
