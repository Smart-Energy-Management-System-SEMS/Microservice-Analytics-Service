"""Domain command: CreateBillPredictionCommand.

In CQRS, a *command* encapsulates the intention to create a bill prediction.
It is an input data-transfer object (input DTO) with no business logic. It is
modeled as a ``dataclass`` with ``slots=True`` for efficiency.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CreateBillPredictionCommand:
    """Data required to request a bill prediction."""

    # --- Required fields ---
    user_id: str                          # User the prediction belongs to
    prediction_year: int                  # Year of the period to predict
    prediction_month: int                 # Month of the period to predict
    period_start: datetime                # Start of the billing period
    period_end: datetime                  # End of the billing period
    historical_consumption_kwh: list[float]  # History used to estimate
    tariff_per_kwh: float                 # Tariff applied per kWh

    # --- Optional fields (with default values) ---
    currency: str = "USD"                 # Currency of the estimated amount
    estimated_kwh: float | None = None    # Pre-estimated kWh (else computed)
    estimated_amount: float | None = None # Pre-estimated amount (else computed)
    error_margin_percentage: float = 10.0 # Prediction error margin (%)
