from dataclasses import dataclass


@dataclass(slots=True)
class CreateDeviceIdentificationCommand:
    user_id: str
    device_id: str
    average_daily_kwh: float | None = None
    predicted_device_type: str | None = None
    confidence_score: float | None = None
    status: str = "completed"
