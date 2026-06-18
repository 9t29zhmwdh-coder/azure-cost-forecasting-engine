"""Cost optimization analyzer: detect RI candidates, anomalies, and growing services."""

from __future__ import annotations

import math
from collections import defaultdict

from .models import DailyCost, ForecastResult, Recommendation

_MIN_DAILY_COST_THRESHOLD = 10.0
_MIN_DATA_DAYS = 14


def analyze(
    daily_costs: list[DailyCost],
    forecast_result: ForecastResult,
) -> list[Recommendation]:
    """Generate prioritized cost optimization recommendations.

    Args:
        daily_costs: Historical daily cost records.
        forecast_result: Forecast used for trend context.

    Returns:
        Recommendations sorted by estimated monthly saving descending.
    """
    recs: list[Recommendation] = []
    recs.extend(_detect_ri_candidates(daily_costs))
    recs.extend(_detect_anomalies(daily_costs))
    recs.extend(_detect_growing_services(daily_costs, forecast_result))
    recs.sort(key=lambda r: r.estimated_monthly_saving, reverse=True)
    return recs


def _service_daily_costs(daily_costs: list[DailyCost]) -> dict[str, list[float]]:
    costs: dict[str, list[float]] = defaultdict(list)
    for day in daily_costs:
        for service, cost in day.by_service.items():
            costs[service].append(cost)
    return dict(costs)


def _detect_ri_candidates(daily_costs: list[DailyCost]) -> list[Recommendation]:
    """Services with stable usage (coefficient of variation < 15%) are RI candidates."""
    recs = []
    for service, costs in _service_daily_costs(daily_costs).items():
        if len(costs) < _MIN_DATA_DAYS:
            continue
        mean = sum(costs) / len(costs)
        if mean < _MIN_DAILY_COST_THRESHOLD:
            continue
        variance = sum((c - mean) ** 2 for c in costs) / len(costs)
        cv = math.sqrt(variance) / mean

        if cv < 0.15:
            monthly_saving = mean * 30 * 0.35
            recs.append(
                Recommendation(
                    service=service,
                    category="reserved_instance",
                    severity="high" if monthly_saving > 100 else "medium",
                    title=f"Reserved Instance candidate: {service}",
                    description=(
                        f"{service} shows highly predictable usage "
                        f"(coefficient of variation {cv:.1%}) over {len(costs)} days. "
                        f"A 1-year Reserved Instance or Savings Plan commitment "
                        f"could reduce this cost by approximately 35%."
                    ),
                    estimated_monthly_saving=round(monthly_saving, 2),
                    estimated_saving_percent=35.0,
                )
            )
    return recs


def _detect_anomalies(daily_costs: list[DailyCost]) -> list[Recommendation]:
    """Services with cost spikes exceeding mean + 2.5 standard deviations."""
    recs = []
    for service, costs in _service_daily_costs(daily_costs).items():
        if len(costs) < _MIN_DATA_DAYS:
            continue
        mean = sum(costs) / len(costs)
        if mean < 5.0:
            continue
        variance = sum((c - mean) ** 2 for c in costs) / len(costs)
        std = math.sqrt(variance)
        if std == 0:
            continue

        spike_days = [(i, c) for i, c in enumerate(costs) if c > mean + 2.5 * std]
        if not spike_days:
            continue

        avg_excess = sum(c - mean for _, c in spike_days) / len(spike_days)
        monthly_saving = avg_excess * (len(spike_days) / len(costs)) * 30
        latest_idx, latest_cost = spike_days[-1]
        date_hint = ""
        if latest_idx < len(daily_costs):
            date_hint = f" (latest: {daily_costs[latest_idx].date})"

        recs.append(
            Recommendation(
                service=service,
                category="anomaly",
                severity="high" if avg_excess > 50 else "medium",
                title=f"Cost spike detected: {service}",
                description=(
                    f"{service} had {len(spike_days)} cost spike(s) exceeding "
                    f"mean + 2.5 standard deviations{date_hint}. "
                    f"Average spike excess: {avg_excess:.2f} per day. "
                    f"Investigate for runaway workloads, misconfigured autoscaling, "
                    f"or unexpected data transfer events."
                ),
                estimated_monthly_saving=round(monthly_saving, 2),
                estimated_saving_percent=round(avg_excess / mean * 100, 1),
            )
        )
    return recs


def _detect_growing_services(
    daily_costs: list[DailyCost], forecast_result: ForecastResult
) -> list[Recommendation]:
    """Services with a daily cost growth rate above 1.5% of their mean."""
    recs = []
    for service, costs in _service_daily_costs(daily_costs).items():
        if len(costs) < _MIN_DATA_DAYS:
            continue
        n = len(costs)
        mean = sum(costs) / n
        if mean < _MIN_DAILY_COST_THRESHOLD:
            continue

        mean_x = (n - 1) / 2
        cov_xy = sum((i - mean_x) * (costs[i] - mean) for i in range(n))
        var_x = sum((i - mean_x) ** 2 for i in range(n))
        slope = cov_xy / var_x if var_x > 0 else 0.0
        slope_pct = slope / mean * 100 if mean > 0 else 0.0

        if slope_pct > 1.5 and mean > _MIN_DAILY_COST_THRESHOLD:
            monthly_impact = slope * 30
            recs.append(
                Recommendation(
                    service=service,
                    category="rightsizing",
                    severity="high" if monthly_impact > 200 else "medium",
                    title=f"Rapidly growing cost: {service}",
                    description=(
                        f"{service} is growing at {slope_pct:.1f}% of its average daily cost per day. "
                        f"Without intervention this will add approximately {monthly_impact:.0f} "
                        f"per month. Review resource scaling policies, autoscaling upper limits, "
                        f"and provisioned capacity that is not actively consumed."
                    ),
                    estimated_monthly_saving=round(monthly_impact * 0.3, 2),
                    estimated_saving_percent=30.0,
                )
            )
    return recs
