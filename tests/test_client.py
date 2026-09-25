import pytest

from acfe import client as client_module
from acfe.client import CostManagementClient, build_query, parse_rows

_COLUMNS = [
    {"name": "PreTaxCost", "type": "Number"},
    {"name": "UsageDate", "type": "Number"},
    {"name": "ServiceName", "type": "String"},
    {"name": "ResourceGroup", "type": "String"},
    {"name": "Currency", "type": "String"},
]


class _Response:
    def __init__(self, status_code: int, payload: dict | None = None, headers=None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.headers = headers or {}

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise client_module.requests.HTTPError(f"{self.status_code} error")


def _client() -> CostManagementClient:
    c = CostManagementClient("tenant", "client", "secret", "sub-123")
    c._token = "token"
    return c


def test_query_asks_for_daily_cost_by_service_and_resource_group() -> None:
    body = build_query("2026-06-01", "2026-08-30")
    assert body["timeframe"] == "Custom"
    assert body["timePeriod"] == {"from": "2026-06-01T00:00:00Z", "to": "2026-08-30T23:59:59Z"}
    assert body["dataset"]["granularity"] == "Daily"
    names = [g["name"] for g in body["dataset"]["grouping"]]
    assert names == ["ServiceName", "ResourceGroup"]


def test_parse_rows_maps_columns_by_name() -> None:
    columns = list(reversed(_COLUMNS))
    rows = [["EUR", "rg-app", "Microsoft.Compute", 20260901, 12.5]]
    (record,) = parse_rows({"columns": columns, "rows": rows})
    assert record.date == "2026-09-01"
    assert record.service_name == "Microsoft.Compute"
    assert record.resource_group == "rg-app"
    assert record.cost == 12.5
    assert record.currency == "EUR"


def test_parse_rows_names_missing_resource_group() -> None:
    (record,) = parse_rows(
        {"columns": _COLUMNS, "rows": [[1.0, 20260901, "Microsoft.Support", "", "USD"]]}
    )
    assert record.resource_group == "(none)"


def test_parse_rows_rejects_unknown_shape() -> None:
    with pytest.raises(ValueError, match="columns"):
        parse_rows({"columns": [{"name": "Foo", "type": "String"}], "rows": [["x"]]})


def test_get_usage_follows_next_link(monkeypatch: pytest.MonkeyPatch) -> None:
    pages = [
        _Response(
            200,
            {
                "properties": {
                    "columns": _COLUMNS,
                    "nextLink": "https://next",
                    "rows": [[1.0, 20260901, "A", "rg", "USD"]],
                }
            },
        ),
        _Response(
            200, {"properties": {"columns": _COLUMNS, "rows": [[2.0, 20260902, "B", "rg", "USD"]]}}
        ),
    ]
    urls = []

    def fake_post(url, **kwargs):
        urls.append(url)
        return pages.pop(0)

    monkeypatch.setattr(client_module.requests, "post", fake_post)
    records = _client().get_usage("2026-09-01", "2026-09-02")
    assert [r.cost for r in records] == [1.0, 2.0]
    assert "/subscriptions/sub-123/providers/Microsoft.CostManagement/query" in urls[0]
    assert urls[1] == "https://next"


def test_get_usage_waits_and_retries_on_throttling(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = [
        _Response(429, headers={"x-ms-ratelimit-microsoft.costmanagement-entity-retry-after": "7"}),
        _Response(200, {"properties": {"columns": _COLUMNS, "rows": []}}),
    ]
    waits = []
    monkeypatch.setattr(client_module.requests, "post", lambda url, **kw: responses.pop(0))
    monkeypatch.setattr(client_module.time, "sleep", waits.append)
    assert _client().get_usage("2026-09-01", "2026-09-02") == []
    assert waits == [7.0]


def test_get_usage_raises_after_repeated_throttling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_module.requests, "post", lambda url, **kw: _Response(429))
    monkeypatch.setattr(client_module.time, "sleep", lambda s: None)
    with pytest.raises(client_module.requests.HTTPError):
        _client().get_usage("2026-09-01", "2026-09-02")


def test_no_content_means_no_records(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(client_module.requests, "post", lambda url, **kw: _Response(204))
    assert _client().get_usage("2026-09-01", "2026-09-02") == []
