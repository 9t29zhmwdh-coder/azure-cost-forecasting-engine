# Changelog

## [0.1.0] (2026-06-18)

### Added

- Azure Consumption API client with OAuth2 client credentials (GET only)
- Usage normalization: per-service daily aggregation and missing-day gap filling
- Forecasting engine: linear regression, Holt two-parameter exponential smoothing, ensemble
- 80% prediction intervals for all forecast points
- Anomaly detection via z-score (configurable threshold, default 2.5)
- Cost optimization analyzer: Reserved Instance candidates, cost spikes, growing services
- Recommendations sorted by estimated monthly saving
- Output formats: terminal table, JSON, Markdown, HTML
- Demo mode with 90-day synthetic Azure usage data (no credentials required)
- CLI: `acfe run [--demo] [--history N] [--format FORMAT] [--output FILE]`
- pytest test suite covering forecasting, normalization and analyzer (35 tests)
- CI pipeline: ubuntu-latest + windows-latest, ruff + pytest
- Sample reports: JSON and Markdown
- Forecasting methodology documentation
- Azure setup guide
