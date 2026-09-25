from datetime import date, timedelta

import acfe.demo as demo
from acfe.analyzer import analyze, analyze_trends
from acfe.models import Anomaly, CostReport, DailyCost, ForecastResult
from acfe.normalizer import fill_missing_days, normalize
from acfe.report import to_html, to_json, to_markdown


def _series(values_by_group: dict[str, list[float]]) -> list[DailyCost]:
    start = date(2026, 1, 1)
    days = len(next(iter(values_by_group.values())))
    result = []
    for i in range(days):
        groups = {name: values[i] for name, values in values_by_group.items()}
        result.append(
            DailyCost(
                date=(start + timedelta(days=i)).isoformat(),
                total_cost=sum(groups.values()),
                by_service={"svc": sum(groups.values())},
                currency="USD",
                by_resource_group=groups,
            )
        )
    return result


def test_normalize_sums_per_resource_group() -> None:
    records = demo.generate(days=3)
    daily = normalize(records)
    assert set(daily[0].by_resource_group) == {"rg-app", "rg-data", "rg-shared"}
    assert abs(sum(daily[0].by_resource_group.values()) - daily[0].total_cost) < 0.01


def test_trend_finds_growing_resource_group() -> None:
    daily = _series({"rg-grow": [100 + 2 * i for i in range(30)], "rg-flat": [50.0] * 30})
    trends = {t.name: t for t in analyze_trends(daily) if t.dimension == "resource_group"}
    assert trends["rg-grow"].direction == "increasing"
    assert trends["rg-flat"].direction == "stable"


def test_trend_ignores_noise_without_slope() -> None:
    noise = [100, 140, 60, 130, 70, 120, 80, 135, 65, 125, 75, 110, 90, 140, 60, 100]
    trends = analyze_trends(_series({"rg-noisy": [float(v) for v in noise]}))
    assert all(t.direction == "stable" for t in trends)


def test_demo_trends_are_the_designed_ones() -> None:
    daily = fill_missing_days(normalize(demo.generate(days=90)))
    moving = {t.name for t in analyze_trends(daily) if t.direction != "stable"}
    assert moving == {"Microsoft.Compute", "Microsoft.Web", "rg-app"}


def test_spike_date_stays_correct_when_service_misses_days() -> None:
    costs = [100.0] * 20
    costs[15] = 900.0
    daily = []
    for i, cost in enumerate(costs):
        by_service = {"steady": 50.0, "spiky": cost} if i >= 5 else {"steady": 50.0}
        daily.append(
            DailyCost(
                date=(date(2026, 1, 1) + timedelta(days=i)).isoformat(),
                total_cost=sum(by_service.values()),
                by_service=by_service,
                currency="USD",
            )
        )
    forecast = ForecastResult(90, 0.0, "stable", 0.0, [], 0.0, 0.0)
    spike = next(r for r in analyze(daily, forecast) if r.category == "anomaly")
    assert "latest: 2026-01-16" in spike.description


def _report() -> CostReport:
    forecast = ForecastResult(30, 10.0, "stable", 0.0, [], 300.0, 0.0)
    daily = _series({"rg-grow": [100 + 2 * i for i in range(30)]})
    return CostReport(
        generated_at="2026-09-25",
        subscription_id="sub",
        history_days=30,
        currency="USD",
        average_daily_cost=10.0,
        total_historical_cost=300.0,
        forecast_30=forecast,
        forecast_60=forecast,
        forecast_90=forecast,
        recommendations=[],
        total_estimated_monthly_saving=0.0,
        anomalies=[Anomaly("2026-09-01", 999.0, 4.2)],
        trends=analyze_trends(daily),
    )


def test_every_report_format_carries_anomalies_and_trends() -> None:
    report = _report()
    for content in (to_json(report), to_markdown(report), to_html(report)):
        assert "2026-09-01" in content
        assert "rg-grow" in content
