# Changelog

## [1.0.0] - 2026-07-18

First stable release: a real release pipeline now builds a wheel/sdist
and attaches it to every GitHub Release, the prerequisite for a 1.0
release per this portfolio's own SemVer discipline.

### Fixed
- The `acfe` console script was broken in any real installed environment: `[project.scripts] acfe = "cli:cli"` pointed at the top-level `cli.py`, but `[tool.setuptools.packages.find]` only packaged the `acfe/` package, so the built wheel never included `cli.py` and the installed command failed with `ModuleNotFoundError: No module named 'cli'`. Added `py-modules = ["cli"]`. Found and fixed by actually installing the built wheel into a fresh virtualenv and running the command, not just building it.
- `acfe --version` reported a hardcoded `"0.1.0"` regardless of the real installed version. Now reads it from package metadata (`importlib.metadata.version(...)`).

### Added
- Release workflow (`release.yml`) that builds a wheel and sdist on every `v*` tag push and attaches them to a GitHub Release. Previously there was no packaged distribution; users had to install from source.

## [0.1.3] (2026-07-12)

### Added

- README/README.de.md: "How it runs" callout, a real screenshot of a demo-generated HTML report (`docs/screenshot.png`), and an "In practice" paragraph, all missing until now.
- README.de.md: "App-Registrierung einrichten" (App Registration Setup), "Optimierungsempfehlungen" (Optimization Recommendations), and "GitHub Action Integration" sections, matching README.md; it was missing all three.
- "Uninstall/Cleanup" section (EN + DE).

### Fixed

- Removed em-dashes/en-dashes from GETTING_STARTED.md.
- Fixed ASCII-substituted umlauts throughout README.de.md ("naechsten", "lueckenlose", "Glaettung", "ueberschreiten", "taeglich", "Vollstaendige", "Benoetigte", "befuellen", "hoeher", "noetig", and more), including one in a section heading.

## [0.1.2] (2026-07-11)

### Added

- Documented Dual-Licensing readiness assessment in ROADMAP.md.

## [0.1.1] (2026-07-11)

### Fixed

- Updated SHA-pinned actions/checkout and actions/setup-python to their latest major versions in CI, since GitHub is deprecating the Node.js 20 runtime and the previously pinned versions (v4.2.2/v5.6.0) were being forced onto Node 24 and crashing during post-run cleanup.

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
