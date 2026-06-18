"""Usage data normalization: aggregate raw records into daily cost summaries."""

from collections import defaultdict
from datetime import date, timedelta

from .models import DailyCost, UsageRecord


def normalize(records: list[UsageRecord]) -> list[DailyCost]:
    """Aggregate usage records into daily totals per service, sorted by date."""
    by_date: dict[str, dict] = defaultdict(
        lambda: {"total": 0.0, "services": defaultdict(float), "currency": "USD"}
    )
    for r in records:
        by_date[r.date]["total"] += r.cost
        by_date[r.date]["services"][r.service_name] += r.cost
        by_date[r.date]["currency"] = r.currency

    result = []
    for day in sorted(by_date):
        d = by_date[day]
        result.append(
            DailyCost(
                date=day,
                total_cost=round(d["total"], 4),
                by_service={k: round(v, 4) for k, v in d["services"].items()},
                currency=d["currency"],
            )
        )
    return result


def fill_missing_days(daily_costs: list[DailyCost]) -> list[DailyCost]:
    """Insert zero-cost entries for any gaps in the time series."""
    if not daily_costs:
        return []
    start = date.fromisoformat(daily_costs[0].date)
    end = date.fromisoformat(daily_costs[-1].date)
    currency = daily_costs[0].currency
    cost_map = {d.date: d for d in daily_costs}
    result = []
    current = start
    while current <= end:
        key = current.isoformat()
        result.append(
            cost_map.get(
                key,
                DailyCost(date=key, total_cost=0.0, by_service={}, currency=currency),
            )
        )
        current += timedelta(days=1)
    return result


def top_services_by_cost(
    daily_costs: list[DailyCost], top_n: int = 10
) -> list[tuple[str, float]]:
    """Return the top N services ranked by total cost over the period."""
    totals: dict[str, float] = defaultdict(float)
    for day in daily_costs:
        for service, cost in day.by_service.items():
            totals[service] += cost
    return sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
