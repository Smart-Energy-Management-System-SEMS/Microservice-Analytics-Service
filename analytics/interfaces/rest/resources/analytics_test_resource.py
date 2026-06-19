from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateEnergyConsumptionTestRequest(BaseModel):
    user_id: str = Field(description="Owner of the device consumption reading.")
    device_id: str = Field(description="Device that produced the reading.")
    energy_kwh: float = Field(ge=0, description="Measured energy consumption in kWh.")
    measured_at: datetime = Field(description="Timestamp of the reading in ISO 8601 format.")
    meter_id: Optional[str] = Field(default=None, description="Optional meter identifier.")
    power_watts: Optional[float] = Field(default=None, ge=0, description="Optional instantaneous power.")
    estimated_cost: Optional[float] = Field(default=None, ge=0, description="Optional precomputed cost.")
    currency: Optional[str] = Field(default=None, description="Currency for generated analytics artifacts.")
    reading_type: Optional[str] = Field(default="manual-test", description="Source of the reading.")


class EnergyConsumptionTestResponse(BaseModel):
    status: str
    message: str
    user_id: str
    device_id: str
    energy_kwh: float
    measured_at: datetime
