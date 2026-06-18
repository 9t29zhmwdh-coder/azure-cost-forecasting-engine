from datetime import date, timedelta

import pytest

from acfe.forecasting import _holt_smoothing, _linear_regression, detect_anomalies, forecast
from acfe.models import DailyCost


def _make_daily(costs: list[float], start: str = "2026-01-01") -> list[DailyCost]:
    start_date = date.fromisoformat(start)
    return [
        DailyCost(
            date=(start_date + timedelta(days=i)).isoformat(),
            total_cost=c,
            by_service={},
            currency="USD",
        )
        for i, c in enumerate(costs)
    ]


def test_stable_trend():
    daily = _make_daily([100.0] * 30)
    result = forecast(daily, horizon_days=30)
    assert result.trend_direction == "stable"
    assert abs(result.points[0].predicted_cost - 100.0) < 10.0


def test_increasing_trend():
    daily = _make_daily([100.0 + i * 3.0 for i in range(30)])
    result = forecast(daily, horizon_days=30)
    assert result.trend_direction == "increasing"
    assert result.projected_total_vs_baseline > 0


def test_decreasing_trend():
    daily = _make_daily([300.0 - i * 3.0 for i in range(30)])
    result = forecast(daily, horizon_days=30)
    assert result.trend_direction == "decreasing"


def test_lower_bound_non_negative():
    daily = _make_daily([50.0 + i * 0.5 for i in range(30)])
    result = forecast(daily, horizon_days=90)
    assert all(p.lower_bound >= 0.0 for p in result.points)


def test_upper_bound_above_predicted():
    daily = _make_daily([100.0] * 30)
    result = forecast(daily, horizon_days=30)
    assert all(p.upper_bound >= p.predicted_cost for p in result.points)


def test_too_few_days_raises():
    with pytest.raises(ValueError, match="At least 7 days"):
        forecast(_make_daily([100.0] * 5), horizon_days=30)


def test_horizon_lengths():
    daily = _make_daily([100.0] * 30)
    for h in (30, 60, 90):
        result = forecast(daily, horizon_days=h)
        assert len(result.points) == h
        assert result.horizon_days == h


def test_linear_regression_perfect_fit():
    slope, intercept = _linear_regression([0.0, 1.0, 2.0], [1.0, 3.0, 5.0])
    assert abs(slope - 2.0) < 1e-9
    assert abs(intercept - 1.0) < 1e-9


def test_holt_smoothing_stable():
    level, trend = _holt_smoothing([100.0] * 20)
    assert abs(level - 100.0) < 5.0
    assert abs(trend) < 2.0


def test_detect_anomalies():
    costs = [100.0] * 20 + [800.0] + [100.0] * 9
    daily = _make_daily(costs)
    anomalies = detect_anomalies(daily)
    assert len(anomalies) == 1
    assert anomalies[0][2] > 2.5  # z-score


def test_detect_no_anomalies_on_stable_data():
    daily = _make_daily([100.0] * 30)
    anomalies = detect_anomalies(daily)
    assert anomalies == []
