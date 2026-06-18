from datetime import date, timedelta

from acfe.analyzer import analyze
from acfe.models import DailyCost, ForecastPoint, ForecastResult


def _make_daily(
    n: int,
    service_costs: dict[str, float],
    start: str = "2026-01-01",
    currency: str = "USD",
) -> list[DailyCost]:
    start_date = date.fromisoformat(start)
    result = []
    for i in range(n):
        day = (start_date + timedelta(days=i)).isoformat()
        by_service = dict(service_costs)
        result.append(
            DailyCost(
                date=day,
                total_cost=sum(by_service.values()),
                by_service=by_service,
                currency=currency,
            )
        )
    return result


def _dummy_forecast(start: str = "2026-05-01") -> ForecastResult:
    start_date = date.fromisoformat(start)
    points = [
        ForecastPoint(
            day_offset=i + 1,
            date=(start_date + timedelta(days=i + 1)).isoformat(),
            predicted_cost=340.0,
            lower_bound=320.0,
            upper_bound=360.0,
        )
        for i in range(90)
    ]
    return ForecastResult(
        horizon_days=90,
        baseline_daily_cost=340.0,
        trend_direction="stable",
        trend_percent_per_day=0.0,
        points=points,
        projected_total=30600.0,
        projected_total_vs_baseline=0.0,
    )


def test_ri_candidate_detected_for_stable_service():
    daily = _make_daily(30, {"Microsoft.Sql": 340.0})
    recs = analyze(daily, _dummy_forecast())
    categories = [r.category for r in recs]
    assert "reserved_instance" in categories


def test_no_ri_for_variable_service():
    import random
    random.seed(99)
    daily = []
    start = date(2026, 1, 1)
    for i in range(30):
        cost = random.uniform(50.0, 500.0)
        daily.append(
            DailyCost(
                date=(start + timedelta(days=i)).isoformat(),
                total_cost=cost,
                by_service={"Microsoft.Compute": cost},
                currency="USD",
            )
        )
    recs = analyze(daily, _dummy_forecast())
    ri_recs = [r for r in recs if r.category == "reserved_instance"]
    assert len(ri_recs) == 0


def test_anomaly_detected_for_spike():
    daily = []
    start = date(2026, 1, 1)
    for i in range(30):
        cost = 1500.0 if i == 15 else 340.0
        daily.append(
            DailyCost(
                date=(start + timedelta(days=i)).isoformat(),
                total_cost=cost,
                by_service={"Microsoft.Compute": cost},
                currency="USD",
            )
        )
    recs = analyze(daily, _dummy_forecast())
    categories = [r.category for r in recs]
    assert "anomaly" in categories


def test_growing_service_detected():
    daily = []
    start = date(2026, 1, 1)
    for i in range(30):
        cost = 100.0 + i * 8.0  # strong growth
        daily.append(
            DailyCost(
                date=(start + timedelta(days=i)).isoformat(),
                total_cost=cost,
                by_service={"Microsoft.Compute": cost},
                currency="USD",
            )
        )
    recs = analyze(daily, _dummy_forecast())
    categories = [r.category for r in recs]
    assert "rightsizing" in categories


def test_recommendations_sorted_by_saving():
    daily = _make_daily(30, {"Microsoft.Sql": 340.0, "Microsoft.Storage": 88.0})
    recs = analyze(daily, _dummy_forecast())
    savings = [r.estimated_monthly_saving for r in recs]
    assert savings == sorted(savings, reverse=True)


def test_no_recs_for_low_cost_service():
    daily = _make_daily(30, {"Microsoft.KeyVault": 1.5})
    recs = analyze(daily, _dummy_forecast())
    assert len(recs) == 0
