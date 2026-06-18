# Roadmap

## v0.1.0 (current)

- [x] Azure Consumption API client with OAuth2 client credentials
- [x] Usage normalization with missing-day gap filling
- [x] Linear regression forecast (30/60/90 days)
- [x] Holt two-parameter exponential smoothing
- [x] Ensemble forecast with 80% prediction intervals
- [x] Anomaly detection via z-score
- [x] Reserved Instance candidate detection (coefficient of variation)
- [x] Rightsizing candidate detection (growth rate)
- [x] Cost spike detection
- [x] Output formats: table, JSON, Markdown, HTML
- [x] Demo mode with synthetic data
- [x] pytest test suite (no credentials required)
- [x] CI pipeline (ubuntu-latest + windows-latest)

## v0.2.0

- [ ] Budget alert integration: compare forecast against defined monthly budget
- [ ] Per-resource-group breakdown in forecasts
- [ ] Multi-subscription aggregation
- [ ] CSV and Excel export
- [ ] `acfe compare` command: compare two time periods

## v0.3.0

- [ ] Azure Cost Management Query API (more granular data)
- [ ] Forecast accuracy tracking: compare previous forecasts against actuals
- [ ] Seasonal decomposition: separate weekly patterns from long-term trend
- [ ] Tag-based cost allocation reports

## v1.0.0

- [ ] Stable CLI API
- [ ] Docker image for containerized runs
- [ ] GitHub Action for automated monthly reports posted as PR comments
- [ ] Jupyter notebook example with chart generation
