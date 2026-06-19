"""Domain command: CreateAnomalyCommand.

In CQRS, a *command* is an immutable object that represents the INTENTION to
change the system state (here, to create an anomaly). It only carries input
data; it holds no business logic.

It is implemented as a ``dataclass`` with ``slots=True`` to lower memory usage
and prevent undeclared attributes.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class CreateAnomalyCommand:
    """Data required to request the creation of an anomaly."""

    # --- Required fields ---
    user_id: str            # User who owns the analyzed consumption
    device_id: str          # Device on which the anomaly is detected
    actual_kwh: float       # Actual measured consumption in kWh

    # --- Optional fields (with default values) ---
    expected_kwh: float | None = None          # Expected consumption (if known)
    historical_kwh: list[float] | None = None  # History used to estimate expected
    threshold_percentage: float = 30.0         # Deviation % that flags an anomaly
    anomaly_type: str | None = None            # Forced type (otherwise computed)
    description: str | None = None             # Manual description (else generated)
