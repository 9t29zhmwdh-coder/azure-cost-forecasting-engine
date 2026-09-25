"""Azure Cost Management Query API client. Credentials exclusively from environment variables."""

from __future__ import annotations

import os
import time

import requests

from .models import UsageRecord

_BASE = "https://management.azure.com"
_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
_API_VERSION = "2023-03-01"
_MAX_RETRIES = 3
_MAX_RETRY_WAIT_SECONDS = 60


def build_query(start_date: str, end_date: str) -> dict:
    """Daily actual cost per service and resource group (the API allows two groupings)."""
    return {
        "type": "ActualCost",
        "timeframe": "Custom",
        "timePeriod": {"from": f"{start_date}T00:00:00Z", "to": f"{end_date}T23:59:59Z"},
        "dataset": {
            "granularity": "Daily",
            "aggregation": {"totalCost": {"name": "PreTaxCost", "function": "Sum"}},
            "grouping": [
                {"type": "Dimension", "name": "ServiceName"},
                {"type": "Dimension", "name": "ResourceGroup"},
            ],
        },
    }


def parse_rows(properties: dict) -> list[UsageRecord]:
    """Map a query result to records by column name, since column order is not guaranteed."""
    if not properties.get("rows"):
        return []
    index = {col["name"].lower(): i for i, col in enumerate(properties.get("columns", []))}
    cost_col = index.get("pretaxcost", index.get("cost"))
    if cost_col is None or "usagedate" not in index:
        raise ValueError(f"Unexpected Cost Management columns: {sorted(index)}")

    def field(row: list, name: str, default: str) -> str:
        position = index.get(name)
        value = row[position] if position is not None else None
        return str(value) if value not in (None, "") else default

    records = []
    for row in properties.get("rows", []):
        day = str(int(row[index["usagedate"]]))  # 20260901 -> 2026-09-01
        records.append(
            UsageRecord(
                date=f"{day[:4]}-{day[4:6]}-{day[6:8]}",
                service_name=field(row, "servicename", "Unknown"),
                resource_group=field(row, "resourcegroup", "(none)"),
                cost=float(row[cost_col]),
                currency=field(row, "currency", "USD"),
                quantity=0.0,
                unit="",
            )
        )
    return records


class CostManagementClient:
    """Read-only client for the Azure Cost Management Query API.

    Microsoft marks the older Consumption UsageDetails API for retirement and
    recommends Cost Management instead; the query also aggregates per day on
    the server, so a subscription with many resources stays a handful of calls.

    Required environment variables:
        AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID

    Required Azure RBAC role at subscription scope:
        Cost Management Reader
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        subscription_id: str,
    ) -> None:
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id
        self._token: str | None = None

    @classmethod
    def from_env(cls) -> CostManagementClient:
        return cls(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
            subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        )

    def _acquire_token(self) -> str:
        url = _TOKEN_URL.format(tenant=self.tenant_id)
        resp = requests.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://management.azure.com/.default",
            },
            timeout=30,
        )
        resp.raise_for_status()
        return str(resp.json()["access_token"])

    def _auth_header(self) -> dict[str, str]:
        if not self._token:
            self._token = self._acquire_token()
        return {"Authorization": f"Bearer {self._token}"}

    def _post(self, url: str, body: dict) -> dict:
        # Cost Management throttles per scope and answers 429 with a wait hint.
        for _ in range(_MAX_RETRIES):
            resp = requests.post(url, json=body, headers=self._auth_header(), timeout=60)
            if resp.status_code != 429:
                break
            time.sleep(min(_retry_after(resp), _MAX_RETRY_WAIT_SECONDS))
        resp.raise_for_status()
        return resp.json() if resp.status_code != 204 else {}

    def get_usage(self, start_date: str, end_date: str) -> list[UsageRecord]:
        """Fetch daily cost per service and resource group for the date range (ISO 8601).

        Follows nextLink until all pages are read.
        """
        body = build_query(start_date, end_date)
        url: str | None = (
            f"{_BASE}/subscriptions/{self.subscription_id}"
            f"/providers/Microsoft.CostManagement/query?api-version={_API_VERSION}"
        )
        records: list[UsageRecord] = []
        while url:
            properties = self._post(url, body).get("properties", {})
            records.extend(parse_rows(properties))
            url = properties.get("nextLink")
        return records


def _retry_after(resp: requests.Response) -> float:
    for header in (
        "x-ms-ratelimit-microsoft.costmanagement-entity-retry-after",
        "x-ms-ratelimit-microsoft.costmanagement-tenant-retry-after",
        "Retry-After",
    ):
        value = resp.headers.get(header)
        if value and value.isdigit():
            return float(value)
    return 10.0
