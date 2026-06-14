"""Event Handler in the Application layer.

Entry point for the integration events arriving from other microservices
(via Kafka). It translates an external event into an internal command and
delegates it to the corresponding Command Service.

It acts as an event "router": it holds no business logic, it only decides
which use case to trigger based on the received ``topic``.
"""

from typing import Any
from datetime import datetime

from analytics.application.commandservices.energy_reading_analytics_command_service import (
    EnergyReadingAnalyticsCommandService,
)
from analytics.domain.model.entities.device_consumption import DeviceConsumption
from analytics.infrastructure.messaging.kafka import events


class AnalyticsEventHandler:
    """Reacts to external events by triggering the proper use cases."""

    def __init__(
        self,
        energy_reading_analytics_command_service: EnergyReadingAnalyticsCommandService,
    ):
        # The command services this handler is allowed to invoke are injected.
        self._energy_reading_analytics_command_service = energy_reading_analytics_command_service

    async def handle(self, topic: str, payload: dict[str, Any]) -> None:
        """Dispatch the event to the right internal handler based on eventType."""
        if topic not in events.CONSUMED_TOPICS:
            return
        event_type = _coalesce(payload, "eventType", "event_type")
        if event_type not in events.CONSUMED_EVENT_TYPES:
            return
        event_payload = _extract_event_payload(payload)
        if event_type == events.ENERGY_READING_CREATED:
            await self._handle_energy_reading_created(event_payload)

    async def _handle_energy_reading_created(self, payload: dict[str, Any]) -> None:
        """Process energy-reading-created events."""
        user_id = _coalesce(payload, "user_id", "userId")
        device_id = _coalesce(payload, "device_id", "deviceId")
        actual_kwh = _coalesce(
            payload,
            "actual_kwh",
            "consumption_kwh",
            "consumptionKwh",
            "energy_kwh",
            "energyKwh",
        )
        measured_at = _coalesce(payload, "timestamp", "occurred_at", "occurredAt", "measured_at", "measuredAt")
        user_id = user_id or _coalesce(payload, "owner_id", "ownerId")

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


def _extract_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
    nested = payload.get("data")
    if not isinstance(nested, dict):
        return payload
    flattened = dict(payload)
    flattened.pop("data", None)
    flattened.update(nested)
    return flattened


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _to_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
