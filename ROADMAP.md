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
- [ ] Azure Cost Management budget threshold notifications via webhook
- [ ] Per-resource-group breakdown in forecasts
- [ ] Multi-subscription aggregation
- [ ] CSV and Excel / Power BI-compatible export
- [ ] `acfe compare` command: compare two time periods

## v0.3.0

- [ ] Azure Cost Management Query API (more granular data)
- [ ] Azure Monitor integration: push anomaly alerts to Log Analytics or Action Groups
- [ ] Forecast accuracy tracking: compare previous forecasts against actuals
- [ ] Seasonal decomposition: separate weekly patterns from long-term trend
- [ ] Tag-based cost allocation reports
- [ ] Power BI dataset export via Azure Blob Storage

## v1.0.0

- [ ] Stable CLI API
- [ ] Docker image for containerized runs
- [ ] GitHub Action for automated monthly reports posted as PR comments
- [ ] Jupyter notebook example with chart generation

## Dual-Licensing Readiness

Assessed 2026-07-11 as a Dual-Licensing candidate (Community MIT + Commercial/Enterprise tier): FinOps cost forecasting for cloud teams is an established commercial category (CloudHealth, Vantage and similar tools already charge for this exact feature set), and ACFE's own roadmap already lists several classic enterprise differentiators. Not ready yet; blocked on:

- [ ] No multi-subscription or multi-tenant aggregation yet (v0.2.0 item above): an Enterprise tier's core value here is usually consolidated, cross-subscription reporting
- [ ] No server or API component to gate a Commercial tier against: today ACFE is a pure local CLI with no persistence layer
- [ ] Enterprise-shaped features (Power BI/Excel export, Azure Monitor push integration, budget/webhook alerts, forecast-accuracy tracking) are still only roadmap entries, not implemented

Once multi-subscription aggregation (v0.2.0) and the Power BI/Azure Monitor integrations (v0.3.0) land, revisit: candidate Enterprise-only features would be multi-subscription/tenant aggregation, Power BI/Excel export, Azure Monitor push integration, and budget/webhook alerting, with the core forecasting engine (normalization, regression/Holt ensemble, anomaly detection, CLI) staying Community/MIT.
