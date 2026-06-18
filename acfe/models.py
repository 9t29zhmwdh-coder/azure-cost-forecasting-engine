from dataclasses import dataclass, field


@dataclass
class UsageRecord:
    date: str
    service_name: str
    resource_group: str
    cost: float
    currency: str
    quantity: float
    unit: str


@dataclass
class DailyCost:
    date: str
    total_cost: float
    by_service: dict[str, float]
    currency: str


@dataclass
class ForecastPoint:
    day_offset: int
    date: str
    predicted_cost: float
    lower_bound: float
    upper_bound: float


@dataclass
class ForecastResult:
    horizon_days: int
    baseline_daily_cost: float
    trend_direction: str
    trend_percent_per_day: float
    points: list[ForecastPoint]
    projected_total: float
    projected_total_vs_baseline: float


@dataclass
class Recommendation:
    service: str
    category: str
    severity: str
    title: str
    description: str
    estimated_monthly_saving: float
    estimated_saving_percent: float


@dataclass
class CostReport:
    generated_at: str
    subscription_id: str
    history_days: int
    currency: str
    average_daily_cost: float
    total_historical_cost: float
    forecast_30: ForecastResult
    forecast_60: ForecastResult
    forecast_90: ForecastResult
    recommendations: list[Recommendation]
    total_estimated_monthly_saving: float
