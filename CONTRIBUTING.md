# Contributing

## Development Setup

```bash
git clone https://github.com/9t29zhmwdh-coder/azure-cost-forecasting-engine
cd azure-cost-forecasting-engine
pip install -e ".[dev]"

# Lint
ruff check acfe/ cli.py tests/

# Test
pytest tests/ -v
```

## Adding a New Recommendation Detector

1. Add a function `_detect_<category>(daily_costs) -> list[Recommendation]` in `acfe/analyzer.py`
2. Call it from `analyze()` and extend the list
3. Add at least one `pytest` test in `tests/test_analyzer.py` using `_make_daily()`
4. Document the detection logic in `ARCHITECTURE.md`

## Adding a New Output Format

1. Add a `to_<format>(report: CostReport) -> str` function in `acfe/report.py`
2. Register it in the `output_format` choice list in `cli.py`
3. Add a brief description to the Output Formats table in `README.md`

## Pull Request Requirements

- `ruff check` passes with no errors
- `pytest tests/ -v` passes on both ubuntu-latest and windows-latest
- No credentials or personal data in any committed file
- `CHANGELOG.md` updated
