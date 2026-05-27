from fastapi import APIRouter, Depends

from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.application.queryservices.device_identification_query_service import DeviceIdentificationQueryService
from analytics.domain.model.queries.get_by_user_query import GetByUserQuery
from analytics.interfaces.rest.controllers.dependencies import (
    get_device_identification_command_service,
    get_device_identification_query_service,
)
from analytics.interfaces.rest.resources.device_identification_resource import (
    CreateDeviceIdentificationRequest,
    DeviceIdentificationResponse,
)
from analytics.interfaces.rest.transform import device_identification_transform as transform

router = APIRouter(prefix="/device-identifications", tags=["Device Identifications"])


@router.get("/user/{user_id}", response_model=list[DeviceIdentificationResponse])
async def get_device_identifications_by_user(
    user_id: str,
    query_service: DeviceIdentificationQueryService = Depends(get_device_identification_query_service),
) -> list[DeviceIdentificationResponse]:
    results = await query_service.get_by_user(GetByUserQuery(user_id=user_id))
    return [transform.entity_to_response(result) for result in results]


@router.post("", response_model=DeviceIdentificationResponse, status_code=201)
async def create_device_identification(
    request: CreateDeviceIdentificationRequest,
    command_service: DeviceIdentificationCommandService = Depends(get_device_identification_command_service),
) -> DeviceIdentificationResponse:
    result = await command_service.create(transform.request_to_command(request))
    return transform.entity_to_response(result)
