"""Event Handler in the Application layer.

Entry point for the integration events arriving from other microservices
(via Kafka). It translates an external event into an internal command and
delegates it to the corresponding Command Service.

It acts as an event "router": it holds no business logic, it only decides
which use case to trigger based on the received ``topic``.
"""

from typing import Any
from datetime import datetime

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.energy_reading_analytics_command_service import (
    EnergyReadingAnalyticsCommandService,
)
from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand
from analytics.infrastructure.messaging.kafka import events


class AnalyticsEventHandler:
    """Reacts to external events by triggering the proper use cases."""

    def __init__(
        self,
        device_identification_command_service: DeviceIdentificationCommandService,
        anomaly_command_service: AnomalyCommandService,
        energy_reading_analytics_command_service: EnergyReadingAnalyticsCommandService,
    ):
        # The command services this handler is allowed to invoke are injected.
        self._device_identification_command_service = device_identification_command_service
        self._anomaly_command_service = anomaly_command_service
        self._energy_reading_analytics_command_service = energy_reading_analytics_command_service

    async def handle(self, topic: str, payload: dict[str, Any]) -> None:
        """Dispatch the event to the right internal handler based on its topic."""
        # Device-related events -> device identification.
        if topic in {events.DEVICE_REGISTERED, events.DEVICE_STATUS_UPDATED}:
            await self._handle_device_event(payload)
        # Energy-reading event -> anomaly detection.
        if topic == events.ENERGY_READING_CREATED:
            await self._handle_energy_reading_created(payload)

    async def _handle_device_event(self, payload: dict[str, Any]) -> None:
        """Process device registered/updated events."""
        user_id = _coalesce(payload, "user_id", "userId")
        device_id = _coalesce(payload, "device_id", "deviceId")
        if not user_id or not device_id:
            return
        # Translate the external payload into an internal command and run it.
        await self._device_identification_command_service.create(
            CreateDeviceIdentificationCommand(
                user_id=str(user_id),
                device_id=str(device_id),
                average_daily_kwh=_to_optional_float(
                    _coalesce(payload, "average_daily_kwh", "averageDailyKwh")
                ),
            )
        )

    async def _handle_energy_reading_created(self, payload: dict[str, Any]) -> None:
        """Process energy-reading-created events."""
        user_id = _coalesce(payload, "user_id", "userId")
        device_id = _coalesce(payload, "device_id", "deviceId")
        actual_kwh = _coalesce(payload, "actual_kwh", "energy_kwh", "energyKwh")
        measured_at = _coalesce(payload, "timestamp", "occurred_at", "occurredAt", "measured_at", "measuredAt")

        # Validation: user_id, device_id, reading timestamp, and measured consumption are required.
        if not user_id or not device_id or actual_kwh is None or measured_at is None:
            return

        await self._energy_reading_analytics_command_service.process(
            DeviceConsumption(
                user_id=str(user_id),
                device_id=str(device_id),
                meter_id=_coalesce(payload, "meter_id", "meterId"),
                power_watts=_to_optional_float(_coalesce(payload, "power_watts", "powerWatts")),
                energy_kwh=float(actual_kwh),
                estimated_cost=_to_optional_float(_coalesce(payload, "estimated_cost", "estimatedCost")),
                currency=_coalesce(payload, "currency"),
                measured_at=_parse_datetime(str(measured_at)),
                reading_type=_coalesce(payload, "reading_type", "readingType"),
                created_at=datetime.utcnow(),
            )
        )


def _coalesce(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return None


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _to_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
