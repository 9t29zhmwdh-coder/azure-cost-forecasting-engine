# Changelog

## [1.0.3] - 2026-07-28

### Added

- `.github/dependabot.yml`, with grouped weekly updates. The file was missing, and without it there are no version updates at all: repository security alerts only fire for disclosed vulnerabilities, which is how action pins across this portfolio quietly went stale. Follows `engineering-standards` v0.10.0.

### Fixed

- 2 action references used a mutable version tag rather than a commit SHA. A tag can be moved to point at different code after the fact without the workflow file changing; a SHA cannot. All are now pinned, with the version in the comment, per `standards/ci-cd.md` section 2. Pinned at the version that was actually running rather than upgraded, so any major bump arrives as its own reviewable Dependabot PR.
- `actions/checkout` pins now carry the full version in the comment instead of a bare major, and all workflows use the same SHA.

## [1.0.2] - 2026-07-28

### Fixed

- CI ran `ruff check acfe/ cli.py tests/`, a path list that left `examples/run_demo.py` unchecked. Nothing was hiding there, it is clean, but any future code in `examples/` would have gone unreviewed. CI now checks the whole tree. See `engineering-standards` `standards/ci-cd.md` section 3: a stage is not kept green by narrowing what it looks at.
- Added `ruff format --check` to CI, which did not exist. It reformatted 5 files, all of it cosmetic line breaks and blank lines. 24 tests pass unchanged.

### Changed

- `ruff` is pinned to 0.16.0 instead of `>=0.4`. Without the pin the format check just added could turn red on unchanged source as soon as a new ruff changes what it considers formatted, per `engineering-standards` v0.7.0.

## [1.0.1] - 2026-07-20

### Changed

- OpenSSF Scorecard workflow and badge.
- `copilot-instructions.md` for consistent AI-assisted contributions.
- Fixed the stale `__version__` string in `acfe/__init__.py` (was 0.1.0, now matches the packaged version).
- Split the README's security/CI badges onto their own line, separate from the platform/tech/AI badges (they were rendering as a single merged line).

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
