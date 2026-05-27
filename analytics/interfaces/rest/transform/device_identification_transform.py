from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand
from analytics.domain.model.entities.device_identification_result import DeviceIdentificationResult
from analytics.interfaces.rest.resources.device_identification_resource import (
    CreateDeviceIdentificationRequest,
    DeviceIdentificationResponse,
)


def request_to_command(request: CreateDeviceIdentificationRequest) -> CreateDeviceIdentificationCommand:
    return CreateDeviceIdentificationCommand(**request.model_dump())


def entity_to_response(entity: DeviceIdentificationResult) -> DeviceIdentificationResponse:
    return DeviceIdentificationResponse(**entity.__dict__)
