<div align="center">
  <img src="RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Architecture</h1>
</div>

## Module Layout

```
azure-cost-forecasting-engine/
├── acfe/
│   ├── models.py        Shared dataclasses (UsageRecord, DailyCost, ForecastResult, CostReport)
│   ├── client.py        Azure Consumption API REST client (OAuth2 client credentials)
│   ├── normalizer.py    Aggregate raw records into DailyCost time series
│   ├── forecasting.py   Forecast engine: linear regression + Holt smoothing + anomaly detection
│   ├── analyzer.py      Cost optimization: RI candidates, anomalies, growing services
│   ├── report.py        Serialization: JSON, Markdown, HTML
│   └── demo.py          Synthetic demo data generator (no credentials required)
├── cli.py               Click CLI: acfe run [--demo] [--format FORMAT] [--output FILE]
├── tests/               pytest test suite (no Azure credentials needed)
├── examples/            Programmatic usage example
├── reports/             Pre-generated sample outputs
└── docs/                Forecasting methodology, Azure setup guide
```

## Data Flow

```
Azure Consumption API  (or demo.generate())
          |
          v
  client.get_usage(start, end)
          |  Produces: list[UsageRecord]
          v
  normalizer.normalize()
          |  Aggregates per (date, service)
          v
  normalizer.fill_missing_days()
          |  Produces: list[DailyCost] (continuous time series)
          v
  forecasting.forecast(daily, horizon=30/60/90)
          |  Linear regression + Holt smoothing ensemble
          |  Produces: ForecastResult with per-day points and bounds
          v
  forecasting.detect_anomalies(daily)
          |  Z-score based spike detection
          |  Produces: list[(date, cost, z_score)]
          v
  analyzer.analyze(daily, forecast)
          |  RI candidates, anomalies, growing services
          |  Produces: list[Recommendation] sorted by saving
          v
  CostReport assembled
          |
          v
  report.to_json() / to_markdown() / to_html()
          |
          v
  stdout or file
```

## Key Algorithms

### Linear Regression (OLS)

Fits slope and intercept to the full history using the closed-form solution. Extrapolates forward for each forecast day.

### Holt Two-Parameter Exponential Smoothing

Level and trend components updated at each time step:

```
level_t = alpha * y_t + (1 - alpha) * (level_{t-1} + trend_{t-1})
trend_t = beta  * (level_t - level_{t-1}) + (1 - beta) * trend_{t-1}
forecast_t+h = level_t + h * trend_t
```

Default: `alpha=0.3`, `beta=0.1`.

### Confidence Interval

80% prediction interval based on RMSE of regression residuals, widening with horizon:

```
margin = 1.28 * RMSE * sqrt(1 + i / n)
```

### RI Detection

Coefficient of variation (CV = std / mean) below 15% over 14+ days signals stable, predictable usage suitable for a Reserved Instance or Savings Plan commitment.

## Adding a New Recommendation Category

1. Add a detector function in `acfe/analyzer.py` returning `list[Recommendation]`
2. Call it from `analyze()` and extend the result list
3. Add a test in `tests/test_analyzer.py` using `_make_daily()`
