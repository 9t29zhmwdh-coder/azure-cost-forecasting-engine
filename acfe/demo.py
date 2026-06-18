"""Synthetic demo data generator. No Azure credentials required."""

from __future__ import annotations

import random
from datetime import date, timedelta

from .models import UsageRecord

_SERVICES: dict[str, dict] = {
    "Microsoft.Compute": {"base": 1180.0, "growth_per_day": 4.2, "noise_std": 85.0},
    "Microsoft.Sql": {"base": 342.0, "growth_per_day": 0.0, "noise_std": 7.0},
    "Microsoft.Storage": {"base": 88.0, "growth_per_day": 0.0, "noise_std": 4.0},
    "Microsoft.Web": {"base": 153.0, "growth_per_day": 0.6, "noise_std": 14.0},
    "Microsoft.Network": {"base": 29.0, "growth_per_day": 0.0, "noise_std": 18.0},
    "Microsoft.Monitor": {"base": 46.0, "growth_per_day": 0.0, "noise_std": 3.0},
    "Microsoft.KeyVault": {"base": 5.2, "growth_per_day": 0.0, "noise_std": 0.5},
}

_ANOMALY_DAY_OFFSET = 62
_ANOMALY_SERVICE = "Microsoft.Compute"
_ANOMALY_MULTIPLIER = 3.4


def generate(days: int = 90, seed: int = 42) -> list[UsageRecord]:
    """Generate `days` days of realistic synthetic Azure usage records.

    Includes:
    - Two stable services (RI candidates): Sql, Storage
    - Two growing services (rightsizing): Compute, Web
    - One anomaly spike on day 62: Compute
    - Variable network costs
    """
    random.seed(seed)
    records: list[UsageRecord] = []
    start = date.today() - timedelta(days=days)

    for i in range(days):
        day = (start + timedelta(days=i)).isoformat()
        for service, cfg in _SERVICES.items():
            base = cfg["base"] + cfg["growth_per_day"] * i
            noise = random.gauss(0, cfg["noise_std"])
            cost = max(0.0, base + noise)

            if i == _ANOMALY_DAY_OFFSET and service == _ANOMALY_SERVICE:
                cost *= _ANOMALY_MULTIPLIER

            records.append(
                UsageRecord(
                    date=day,
                    service_name=service,
                    resource_group="rg-production",
                    cost=round(cost, 4),
                    currency="USD",
                    quantity=round(cost / 10, 2),
                    unit="1 Unit",
                )
            )

    return records
