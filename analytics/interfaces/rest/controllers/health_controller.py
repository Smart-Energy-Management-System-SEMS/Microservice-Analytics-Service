from fastapi import APIRouter

from analytics.interfaces.rest.resources.health_resource import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="UP", service="analytics-service", version="1.0.0")
