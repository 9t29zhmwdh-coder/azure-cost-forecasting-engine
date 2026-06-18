<div align="center">
  <img src="../RayStudio.png" alt="RayStudio Logo" width="120"/>
  <h1>Forecasting Methodology</h1>
</div>

## Overview

The forecasting engine combines two time-series models in an ensemble to produce a single
prediction with confidence bounds. Neither model requires external numerical libraries.

## Linear Regression (Ordinary Least Squares)

Fits a straight line through all historical daily cost points using the closed-form OLS solution:

```
slope     = (n * sum(x*y) - sum(x) * sum(y)) / (n * sum(x^2) - sum(x)^2)
intercept = (sum(y) - slope * sum(x)) / n
```

Where `x` is the day index (0, 1, 2, ...) and `y` is the daily total cost.

Forecast for day `t`: `predicted = intercept + slope * t`

Strengths: captures overall trend direction reliably.
Weaknesses: gives equal weight to old and new data; does not adapt to recent shifts.

## Holt Two-Parameter Exponential Smoothing

Updates level and trend components at each time step:

```
level_t = alpha * y_t + (1 - alpha) * (level_{t-1} + trend_{t-1})
trend_t = beta  * (level_t - level_{t-1}) + (1 - beta) * trend_{t-1}
```

Forecast for `h` steps ahead: `predicted = level_t + h * trend_t`

Default parameters: `alpha = 0.3`, `beta = 0.1`. These are conservative values that
favour stability over sensitivity to individual outliers.

Strengths: adapts to recent trend changes; more responsive than pure regression.
Weaknesses: may overreact to short-term spikes.

## Ensemble

Final forecast is the arithmetic mean of both models:

```
ensemble = (linear_regression_pred + holt_pred) / 2
```

This reduces the risk of either model alone dominating a misleading signal.

## Confidence Intervals

Based on the RMSE of regression residuals (how far actual costs deviated from the
regression line in historical data):

```
margin = 1.28 * RMSE * sqrt(1 + i / n)
```

Where `i` is the forecast step and `n` is the number of historical days.
The factor `1.28` corresponds to the 80% two-sided z-interval. The interval widens
naturally as the forecast extends further into the future.

## Anomaly Detection

For each day in the historical period, compute a z-score relative to the full-period mean and standard deviation:

```
z = (cost - mean) / std
```

Days with `z > threshold` (default `2.5`) are flagged as anomalies. A threshold of 2.5
corresponds to approximately 99.4% of a normal distribution, minimizing false positives
while catching genuine spikes.

## Baseline

The baseline daily cost is the arithmetic mean of the most recent 30 days (or all available
days if fewer than 30 are provided). It is used for:

- Trend direction classification (stable: change below 0.5% per day)
- The vs-baseline delta in forecast output
- Reserved Instance saving estimates (baseline * 30 * 0.35)
