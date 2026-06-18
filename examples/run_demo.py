"""Minimal example: run the full pipeline with synthetic demo data.

Usage:
    python examples/run_demo.py

No Azure credentials required. Output is printed to stdout.
"""

import sys
from pathlib import Path

# Allow running from the repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from acfe import demo
from acfe.analyzer import analyze
from acfe.forecasting import detect_anomalies, forecast
from acfe.models import CostReport
from acfe.normalizer import fill_missing_days, normalize
from acfe.report import to_markdown

HISTORY_DAYS = 90

records = demo.generate(days=HISTORY_DAYS)
print(f"Generated {len(records)} usage records over {HISTORY_DAYS} days.")

daily = fill_missing_days(normalize(records))
total_cost = sum(d.total_cost for d in daily)
avg_daily = total_cost / len(daily)

fc30 = forecast(daily, horizon_days=30)
fc60 = forecast(daily, horizon_days=60)
fc90 = forecast(daily, horizon_days=90)

anomalies = detect_anomalies(daily)
print(f"Anomalies detected: {len(anomalies)}")

recommendations = analyze(daily, fc90)
total_saving = sum(r.estimated_monthly_saving for r in recommendations)
print(f"Recommendations: {len(recommendations)} (est. monthly saving: {total_saving:.2f})")

report = CostReport(
    generated_at="2026-06-18",
    subscription_id="demo-subscription",
    history_days=len(daily),
    currency="USD",
    average_daily_cost=round(avg_daily, 2),
    total_historical_cost=round(total_cost, 2),
    forecast_30=fc30,
    forecast_60=fc60,
    forecast_90=fc90,
    recommendations=recommendations,
    total_estimated_monthly_saving=round(total_saving, 2),
)

print("\n" + to_markdown(report))
