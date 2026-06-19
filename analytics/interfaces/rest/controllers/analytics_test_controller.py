from datetime import datetime

from fastapi import APIRouter, Depends

from analytics.application.commandservices.energy_reading_analytics_command_service import (
    EnergyReadingAnalyticsCommandService,
)
from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.interfaces.rest.controllers.dependencies import get_energy_reading_analytics_command_service
from analytics.interfaces.rest.resources.analytics_test_resource import (
    CreateEnergyConsumptionTestRequest,
    EnergyConsumptionTestResponse,
)

router = APIRouter(prefix="/test", tags=["Analytics Test"])


@router.post(
    "/energy-consumption-recorded",
    response_model=EnergyConsumptionTestResponse,
    status_code=202,
    summary="Simulate an energy consumption event",
    description=(
        "Manual smoke-test endpoint for Swagger/Postman. It executes the same analytics flow "
        "triggered by the Kafka event `energy.consumption.recorded`."
    ),
)
async def simulate_energy_consumption_recorded(
    request: CreateEnergyConsumptionTestRequest,
    command_service: EnergyReadingAnalyticsCommandService = Depends(get_energy_reading_analytics_command_service),
) -> EnergyConsumptionTestResponse:
    await command_service.process(
        DeviceConsumption(
            user_id=request.user_id,
            device_id=request.device_id,
            energy_kwh=request.energy_kwh,
            measured_at=request.measured_at,
            created_at=datetime.utcnow(),
            meter_id=request.meter_id,
            power_watts=request.power_watts,
            estimated_cost=request.estimated_cost,
            currency=request.currency,
            reading_type=request.reading_type,
        )
    )
    return EnergyConsumptionTestResponse(
        status="accepted",
        message=(
            "Reading processed. Check bill predictions, recommendations, anomalies, "
            "and consumption rankings for this user."
        ),
        user_id=request.user_id,
        device_id=request.device_id,
        energy_kwh=request.energy_kwh,
        measured_at=request.measured_at,
    )
