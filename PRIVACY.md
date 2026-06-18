# Privacy

Azure Cost Forecasting Engine processes Azure billing data locally on your machine.

- All data processing happens in memory on your local machine or CI runner.
- No usage data, cost figures, subscription IDs, or tenant IDs are sent to any third-party service.
- The Azure Consumption API is contacted only to fetch your own subscription's billing data.
- Report files are written only when explicitly requested via `--output`.
- The `--demo` mode uses fully synthetic data and makes no network requests at all.
- No analytics, telemetry, or error reporting is collected.
