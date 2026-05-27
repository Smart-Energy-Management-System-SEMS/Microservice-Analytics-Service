from typing import Any

from analytics.application.commandservices.anomaly_command_service import AnomalyCommandService
from analytics.application.commandservices.device_identification_command_service import DeviceIdentificationCommandService
from analytics.domain.model.commands.create_anomaly_command import CreateAnomalyCommand
from analytics.domain.model.commands.create_device_identification_command import CreateDeviceIdentificationCommand


class AnalyticsEventHandler:
    def __init__(
        self,
        device_identification_command_service: DeviceIdentificationCommandService,
        anomaly_command_service: AnomalyCommandService,
    ):
        self._device_identification_command_service = device_identification_command_service
        self._anomaly_command_service = anomaly_command_service

    async def handle(self, topic: str, payload: dict[str, Any]) -> None:
        if topic in {"device.registered", "device.updated"}:
            await self._handle_device_event(payload)
        if topic == "energy.consumption.recorded":
            await self._handle_consumption_recorded(payload)

    async def _handle_device_event(self, payload: dict[str, Any]) -> None:
        if not payload.get("user_id") or not payload.get("device_id"):
            return
        await self._device_identification_command_service.create(
            CreateDeviceIdentificationCommand(
                user_id=str(payload["user_id"]),
                device_id=str(payload["device_id"]),
                average_daily_kwh=payload.get("average_daily_kwh"),
            )
        )

    async def _handle_consumption_recorded(self, payload: dict[str, Any]) -> None:
        if not payload.get("user_id") or not payload.get("device_id") or payload.get("actual_kwh") is None:
            return
        await self._anomaly_command_service.create(
            CreateAnomalyCommand(
                user_id=str(payload["user_id"]),
                device_id=str(payload["device_id"]),
                actual_kwh=float(payload["actual_kwh"]),
                expected_kwh=payload.get("expected_kwh"),
                historical_kwh=payload.get("historical_kwh") or [],
            )
        )
