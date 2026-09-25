"""Cost optimization analyzer: detect RI candidates, anomalies, and growing services."""

from __future__ import annotations

import math

from .models import DailyCost, ForecastResult, Recommendation, Trend

_MIN_DAILY_COST_THRESHOLD = 10.0
_MIN_DATA_DAYS = 14
# Linear growth as a share of the average daily cost. 0.25% a day adds roughly
# 7.5% a month; the earlier 1.5% meant doubling within about 50 days and so
# never fired on real spend.
_GROWTH_PCT_PER_DAY = 0.25
# Roughly 95% confidence that the slope is not noise.
_MIN_TREND_T_STAT = 2.0


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
    """One value per day for every service, 0 where it had no cost.

    Keeping the series aligned with `daily_costs` makes index i the same date
    for every service, which the anomaly date and the growth slope rely on.
    """
    return _aligned_series(daily_costs, lambda day: day.by_service)


def _aligned_series(daily_costs: list[DailyCost], values_of) -> dict[str, list[float]]:
    names = {name for day in daily_costs for name in values_of(day)}
    return {name: [values_of(day).get(name, 0.0) for day in daily_costs] for name in names}


def _fit(costs: list[float]) -> tuple[float, float]:
    """Least-squares slope and its t-statistic.

    Daily cost is noisy, and a slope fitted to pure noise is never exactly 0;
    the t-statistic tells a real trend from a line through the scatter.
    """
    n = len(costs)
    mean_x = (n - 1) / 2
    mean_y = sum(costs) / n
    var_x = sum((i - mean_x) ** 2 for i in range(n))
    if n < 3 or var_x == 0:
        return 0.0, 0.0
    slope = sum((i - mean_x) * (costs[i] - mean_y) for i in range(n)) / var_x
    intercept = mean_y - slope * mean_x
    residual = sum((costs[i] - intercept - slope * i) ** 2 for i in range(n))
    std_error = math.sqrt(residual / (n - 2) / var_x)
    return slope, (slope / std_error if std_error > 0 else math.inf)


def _direction(percent_per_day: float) -> str:
    if percent_per_day > _GROWTH_PCT_PER_DAY:
        return "increasing"
    if percent_per_day < -_GROWTH_PCT_PER_DAY:
        return "decreasing"
    return "stable"


def _is_significant(t_stat: float) -> bool:
    return abs(t_stat) >= _MIN_TREND_T_STAT


def analyze_trends(daily_costs: list[DailyCost]) -> list[Trend]:
    """Trend per service and per resource group, fastest growing first."""
    trends = []
    for dimension, values_of in (
        ("service", lambda day: day.by_service),
        ("resource_group", lambda day: day.by_resource_group),
    ):
        for name, costs in _aligned_series(daily_costs, values_of).items():
            mean = sum(costs) / len(costs)
            if len(costs) < _MIN_DATA_DAYS or mean <= 0:
                continue
            slope, t_stat = _fit(costs)
            pct = slope / mean * 100
            direction = _direction(pct) if _is_significant(t_stat) else "stable"
            trends.append(Trend(dimension, name, direction, round(pct, 3), round(mean, 2)))
    return sorted(trends, key=lambda t: t.percent_per_day, reverse=True)


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
        latest_idx, _ = spike_days[-1]
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
    """Services whose cost grows by more than _GROWTH_PCT_PER_DAY of their mean per day."""
    recs = []
    for service, costs in _service_daily_costs(daily_costs).items():
        if len(costs) < _MIN_DATA_DAYS:
            continue
        mean = sum(costs) / len(costs)
        if mean < _MIN_DAILY_COST_THRESHOLD:
            continue

        slope, t_stat = _fit(costs)
        slope_pct = slope / mean * 100

        if slope_pct > _GROWTH_PCT_PER_DAY and _is_significant(t_stat):
            monthly_impact = slope * 30
            recs.append(
                Recommendation(
                    service=service,
                    category="rightsizing",
                    severity="high" if monthly_impact > 200 else "medium",
                    title=f"Growing cost: {service}",
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
