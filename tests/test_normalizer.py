from acfe.models import UsageRecord
from acfe.normalizer import fill_missing_days, normalize, top_services_by_cost


def _rec(day: str, service: str, cost: float) -> UsageRecord:
    return UsageRecord(
        date=day,
        service_name=service,
        resource_group="rg",
        cost=cost,
        currency="USD",
        quantity=1.0,
        unit="Unit",
    )


def test_normalize_aggregates_same_day():
    records = [
        _rec("2026-01-01", "VM", 100.0),
        _rec("2026-01-01", "Storage", 20.0),
        _rec("2026-01-02", "VM", 110.0),
    ]
    result = normalize(records)
    assert len(result) == 2
    assert abs(result[0].total_cost - 120.0) < 0.01
    assert abs(result[1].total_cost - 110.0) < 0.01


def test_normalize_by_service():
    records = [
        _rec("2026-01-01", "VM", 100.0),
        _rec("2026-01-01", "Storage", 20.0),
    ]
    result = normalize(records)
    assert abs(result[0].by_service["VM"] - 100.0) < 0.01
    assert abs(result[0].by_service["Storage"] - 20.0) < 0.01


def test_normalize_sorted_by_date():
    records = [
        _rec("2026-01-03", "VM", 100.0),
        _rec("2026-01-01", "VM", 80.0),
        _rec("2026-01-02", "VM", 90.0),
    ]
    result = normalize(records)
    assert result[0].date == "2026-01-01"
    assert result[2].date == "2026-01-03"


def test_fill_missing_days_inserts_zeros():
    records = [
        _rec("2026-01-01", "VM", 100.0),
        _rec("2026-01-03", "VM", 100.0),
    ]
    daily = normalize(records)
    filled = fill_missing_days(daily)
    assert len(filled) == 3
    assert filled[1].date == "2026-01-02"
    assert filled[1].total_cost == 0.0


def test_fill_missing_days_empty():
    assert fill_missing_days([]) == []


def test_fill_missing_days_no_gap():
    records = [_rec(f"2026-01-0{i}", "VM", 100.0) for i in range(1, 4)]
    daily = normalize(records)
    filled = fill_missing_days(daily)
    assert len(filled) == 3


def test_top_services_by_cost():
    records = [
        _rec("2026-01-01", "VM", 500.0),
        _rec("2026-01-01", "Storage", 50.0),
        _rec("2026-01-02", "VM", 600.0),
    ]
    daily = normalize(records)
    top = top_services_by_cost(daily, top_n=2)
    assert top[0][0] == "VM"
    assert abs(top[0][1] - 1100.0) < 0.01
