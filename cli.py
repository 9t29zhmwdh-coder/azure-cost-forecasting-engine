"""Azure Cost Forecasting Engine - CLI entry point."""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from pathlib import Path

import click

import acfe.demo as demo_data
from acfe.analyzer import analyze
from acfe.client import ConsumptionClient
from acfe.forecasting import detect_anomalies, forecast
from acfe.models import CostReport
from acfe.normalizer import fill_missing_days, normalize, top_services_by_cost
from acfe.report import to_html, to_json, to_markdown


@click.group()
@click.version_option("0.1.0", prog_name="acfe")
def cli() -> None:
    """Azure Cost Forecasting Engine.

    Analyze historical Azure costs and forecast the next 30, 60 and 90 days.
    Use --demo to run without Azure credentials.
    """


@cli.command("run")
@click.option(
    "--demo",
    is_flag=True,
    help="Use built-in synthetic data (no Azure credentials required).",
)
@click.option(
    "--history",
    default=90,
    show_default=True,
    help="Days of historical usage to fetch.",
)
@click.option(
    "--format",
    "output_format",
    default="table",
    show_default=True,
    type=click.Choice(["table", "json", "md", "html"], case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Write report to FILE instead of stdout.",
)
def run_cmd(
    demo: bool,
    history: int,
    output_format: str,
    output: Path | None,
) -> None:
    """Fetch usage data, forecast costs and generate optimization recommendations."""
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        _load_dotenv(dotenv_path)

    click.echo(f"[acfe] Loading {'demo' if demo else 'Azure'} data...", err=True)

    if demo:
        records = demo_data.generate(days=history)
        subscription_id = "demo-subscription"
    else:
        try:
            client = ConsumptionClient.from_env()
        except KeyError as exc:
            click.echo(
                f"[acfe] Missing environment variable: {exc}. "
                "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, "
                "AZURE_SUBSCRIPTION_ID or use --demo.",
                err=True,
            )
            sys.exit(1)
        subscription_id = client.subscription_id
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=history)).isoformat()
        records = client.get_usage(start, end)

    click.echo(f"[acfe] {len(records)} usage records loaded.", err=True)

    daily = fill_missing_days(normalize(records))
    currency = daily[0].currency if daily else "USD"

    total_cost = sum(d.total_cost for d in daily)
    avg_daily = total_cost / len(daily) if daily else 0.0

    click.echo("[acfe] Running forecast...", err=True)
    fc30 = forecast(daily, horizon_days=30)
    fc60 = forecast(daily, horizon_days=60)
    fc90 = forecast(daily, horizon_days=90)

    anomalies = detect_anomalies(daily)
    if anomalies:
        click.echo(
            f"[acfe] {len(anomalies)} cost anomaly day(s) detected.", err=True
        )

    click.echo("[acfe] Analyzing optimization opportunities...", err=True)
    recommendations = analyze(daily, fc90)
    total_saving = sum(r.estimated_monthly_saving for r in recommendations)

    report = CostReport(
        generated_at=date.today().isoformat(),
        subscription_id=subscription_id,
        history_days=len(daily),
        currency=currency,
        average_daily_cost=round(avg_daily, 2),
        total_historical_cost=round(total_cost, 2),
        forecast_30=fc30,
        forecast_60=fc60,
        forecast_90=fc90,
        recommendations=recommendations,
        total_estimated_monthly_saving=round(total_saving, 2),
    )

    if output_format == "json":
        content = to_json(report)
    elif output_format == "md":
        content = to_markdown(report)
    elif output_format == "html":
        content = to_html(report)
    else:
        content = _render_table(report, daily, anomalies)

    if output:
        output.write_text(content, encoding="utf-8")
        click.echo(f"[acfe] Report written to {output}", err=True)
    else:
        click.echo(content)


def _render_table(
    report: CostReport,
    daily: list,
    anomalies: list,
) -> str:
    lines = [
        "Azure Cost Forecasting Engine",
        "=" * 60,
        f"Subscription : {report.subscription_id}",
        f"History      : {report.history_days} days",
        f"Currency     : {report.currency}",
        f"Avg daily    : {report.average_daily_cost:.2f}",
        f"Total        : {report.total_historical_cost:.2f}",
        "",
        "Forecast",
        "-" * 40,
        f"  30d : {report.forecast_30.projected_total:.2f}  "
        f"({report.forecast_30.projected_total_vs_baseline:+.2f} vs baseline)  "
        f"trend: {report.forecast_30.trend_direction}",
        f"  60d : {report.forecast_60.projected_total:.2f}  "
        f"({report.forecast_60.projected_total_vs_baseline:+.2f} vs baseline)",
        f"  90d : {report.forecast_90.projected_total:.2f}  "
        f"({report.forecast_90.projected_total_vs_baseline:+.2f} vs baseline)",
    ]

    if anomalies:
        lines += ["", "Anomalies detected", "-" * 40]
        for a_date, a_cost, a_z in anomalies[:5]:
            lines.append(f"  {a_date}  cost={a_cost:.2f}  z={a_z:.1f}")

    if report.recommendations:
        lines += [
            "",
            f"Recommendations  (est. total saving: {report.total_estimated_monthly_saving:.2f}/month)",
            "-" * 40,
        ]
        for rec in report.recommendations[:10]:
            icon = "[H]" if rec.severity == "high" else "[M]"
            lines.append(
                f"  {icon} {rec.estimated_monthly_saving:8.2f}/mo  {rec.title}"
            )

    return "\n".join(lines)


def _load_dotenv(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


if __name__ == "__main__":
    cli()
