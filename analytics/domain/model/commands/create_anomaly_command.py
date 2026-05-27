from dataclasses import dataclass


@dataclass(slots=True)
class CreateAnomalyCommand:
    user_id: str
    device_id: str
    actual_kwh: float
    expected_kwh: float | None = None
    historical_kwh: list[float] | None = None
    threshold_percentage: float = 30.0
    anomaly_type: str | None = None
    description: str | None = None
