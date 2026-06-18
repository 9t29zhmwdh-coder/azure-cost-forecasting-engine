"""Forecasting engine: ensemble of linear regression and Holt exponential smoothing."""

from __future__ import annotations

import math
from datetime import date, timedelta

from .models import DailyCost, ForecastPoint, ForecastResult

_MIN_HISTORY_DAYS = 7


def forecast(
    daily_costs: list[DailyCost],
    horizon_days: int = 90,
) -> ForecastResult:
    """Generate a cost forecast for the next `horizon_days` days.

    Uses an ensemble of linear regression and Holt two-parameter exponential
    smoothing. Confidence bounds are derived from historical residual variance.

    Args:
        daily_costs: Sorted list of daily cost records (fill_missing_days recommended).
        horizon_days: Number of days to forecast (typically 30, 60, or 90).

    Returns:
        ForecastResult with per-day predictions and 80% prediction intervals.

    Raises:
        ValueError: If fewer than _MIN_HISTORY_DAYS days are provided.
    """
    if len(daily_costs) < _MIN_HISTORY_DAYS:
        raise ValueError(
            f"At least {_MIN_HISTORY_DAYS} days of history required, "
            f"got {len(daily_costs)}."
        )

    costs = [d.total_cost for d in daily_costs]
    n = len(costs)

    lr_slope, lr_intercept = _linear_regression(list(range(n)), costs)
    hl_level, hl_trend = _holt_smoothing(costs)

    mean = sum(costs) / n
    residuals = [c - (lr_intercept + lr_slope * i) for i, c in enumerate(costs)]
    rmse = math.sqrt(sum(r**2 for r in residuals) / n)

    lookback = min(30, n)
    baseline = sum(costs[-lookback:]) / lookback

    trend_pct = lr_slope / baseline * 100 if baseline > 0 else 0.0
    if trend_pct > 0.5:
        trend_direction = "increasing"
    elif trend_pct < -0.5:
        trend_direction = "decreasing"
    else:
        trend_direction = "stable"

    last_date = date.fromisoformat(daily_costs[-1].date)
    points: list[ForecastPoint] = []

    for i in range(1, horizon_days + 1):
        lr_pred = lr_intercept + lr_slope * (n + i - 1)
        holt_pred = hl_level + hl_trend * i
        pred = max(0.0, (lr_pred + holt_pred) / 2)

        # 80% prediction interval widens with forecast distance
        margin = 1.28 * rmse * math.sqrt(1 + i / n)

        forecast_date = (last_date + timedelta(days=i)).isoformat()
        points.append(
            ForecastPoint(
                day_offset=i,
                date=forecast_date,
                predicted_cost=round(pred, 2),
                lower_bound=round(max(0.0, pred - margin), 2),
                upper_bound=round(pred + margin, 2),
            )
        )

    projected_total = sum(p.predicted_cost for p in points)
    baseline_total = baseline * horizon_days

    return ForecastResult(
        horizon_days=horizon_days,
        baseline_daily_cost=round(baseline, 2),
        trend_direction=trend_direction,
        trend_percent_per_day=round(trend_pct, 3),
        points=points,
        projected_total=round(projected_total, 2),
        projected_total_vs_baseline=round(projected_total - baseline_total, 2),
    )


def detect_anomalies(
    daily_costs: list[DailyCost], z_threshold: float = 2.5
) -> list[tuple[str, float, float]]:
    """Return days where total cost exceeds the mean by z_threshold standard deviations.

    Returns:
        List of (date, cost, z_score) tuples, sorted by z_score descending.
    """
    if len(daily_costs) < 7:
        return []
    costs = [d.total_cost for d in daily_costs]
    mean = sum(costs) / len(costs)
    variance = sum((c - mean) ** 2 for c in costs) / len(costs)
    std = math.sqrt(variance)
    if std == 0:
        return []
    anomalies = [
        (d.date, d.total_cost, (d.total_cost - mean) / std)
        for d in daily_costs
        if (d.total_cost - mean) / std > z_threshold
    ]
    return sorted(anomalies, key=lambda x: x[2], reverse=True)


# --- Internal helpers ---

def _linear_regression(x: list[float], y: list[float]) -> tuple[float, float]:
    """Ordinary least-squares linear regression. Returns (slope, intercept)."""
    n = len(x)
    if n < 2:
        return 0.0, y[0] if y else 0.0
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi**2 for xi in x)
    denom = n * sum_x2 - sum_x**2
    if denom == 0:
        return 0.0, sum_y / n
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def _holt_smoothing(
    y: list[float], alpha: float = 0.3, beta: float = 0.1
) -> tuple[float, float]:
    """Holt two-parameter exponential smoothing. Returns (level, trend)."""
    if len(y) < 2:
        return y[0] if y else 0.0, 0.0
    level = y[0]
    trend = y[1] - y[0]
    for value in y[1:]:
        prev_level = level
        level = alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
    return level, trend
