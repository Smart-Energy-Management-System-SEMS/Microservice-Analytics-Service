"""Domain command: CreateConsumptionRankingCommand.

In CQRS, this *command* represents the intention to generate a per-device
consumption ranking for a given user and period. It also defines
``RankingSourceItem``, an input value object holding each device's raw
consumption that the domain will later sort.

Both are modeled as ``dataclass`` with ``slots=True`` (memory efficiency).
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class RankingSourceItem:
    """A device's consumption used as input to build the ranking."""

    device_id: str      # Device identifier
    device_name: str    # Human-readable device name
    total_kwh: float    # Total device consumption in the period


@dataclass(slots=True)
class CreateConsumptionRankingCommand:
    """Data required to request the creation of a consumption ranking."""

    # --- Required fields ---
    user_id: str                       # User who owns the ranking
    period_type: str                   # Period type (daily, monthly, etc.)
    period_start: datetime             # Start of the analyzed period
    period_end: datetime               # End of the analyzed period
    devices: list[RankingSourceItem]   # Devices with their consumption to rank

    # --- Optional fields (with default values) ---
    tariff_per_kwh: float = 0.65       # Tariff per kWh to estimate costs
    currency: str = "USD"              # Currency of the ranking amounts
