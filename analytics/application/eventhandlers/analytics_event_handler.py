"""Event Handler in the Application layer.

Entry point for the integration events arriving from other microservices
(via Kafka). It translates an external event into an internal command and
delegates it to the corresponding Command Service.

It acts as an event "router": it holds no business logic, it only decides
which use case to trigger based on the received ``topic``.
"""

from typing import Any

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand
from analytics.infrastructure.messaging.kafka import events


class AnalyticsEventHandler:
    """Reacts to external events by triggering the proper use cases."""

    def __init__(
        self,
        device_identification_command_service: DeviceIdentificationCommandService,
        anomaly_command_service: AnomalyCommandService,
    ):
        # The command services this handler is allowed to invoke are injected.
        self._device_identification_command_service = device_identification_command_service
        self._anomaly_command_service = anomaly_command_service

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
        # Defensive validation: without user_id or device_id we cannot proceed.
        if not payload.get("user_id") or not payload.get("device_id"):
            return
        # Translate the external payload into an internal command and run it.
        await self._device_identification_command_service.create(
            CreateDeviceIdentificationCommand(
                user_id=str(payload["user_id"]),
                device_id=str(payload["device_id"]),
                average_daily_kwh=payload.get("average_daily_kwh"),
            )
        )

    async def _handle_energy_reading_created(self, payload: dict[str, Any]) -> None:
        """Process energy-reading-created events."""
        actual_kwh = payload.get("actual_kwh")
        if actual_kwh is None:
            actual_kwh = payload.get("energy_kwh")

        # Validation: user_id, device_id, and the measured consumption are required.
        if not payload.get("user_id") or not payload.get("device_id") or actual_kwh is None:
            return
        # detect_and_create only creates the anomaly if the rules detect one.
        await self._anomaly_command_service.detect_and_create(
            CreateAnomalyCommand(
                user_id=str(payload["user_id"]),
                device_id=str(payload["device_id"]),
                actual_kwh=float(actual_kwh),
                expected_kwh=payload.get("expected_kwh"),
                historical_kwh=payload.get("historical_kwh") or [],  # empty list by default
            )
        )
