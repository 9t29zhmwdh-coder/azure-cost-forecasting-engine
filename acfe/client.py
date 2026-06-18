"""Azure Consumption API client. Credentials exclusively from environment variables."""

from __future__ import annotations

import os

import requests

from .models import UsageRecord

_BASE = "https://management.azure.com"
_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"


class ConsumptionClient:
    """Read-only client for the Azure Consumption (UsageDetails) API.

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
    def from_env(cls) -> ConsumptionClient:
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

    def get_usage(self, start_date: str, end_date: str) -> list[UsageRecord]:
        """Fetch daily usage details for the given date range (ISO 8601 strings).

        Handles pagination automatically via nextLink.
        """
        url: str | None = (
            f"{_BASE}/subscriptions/{self.subscription_id}"
            "/providers/Microsoft.Consumption/usageDetails"
            "?api-version=2023-03-01"
            f"&$filter=properties/usageStart ge '{start_date}' "
            f"and properties/usageEnd le '{end_date}'"
        )
        records: list[UsageRecord] = []

        while url:
            resp = requests.get(url, headers=self._auth_header(), timeout=60)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("value", []):
                p = item.get("properties", {})
                records.append(
                    UsageRecord(
                        date=str(p.get("date", ""))[:10],
                        service_name=str(p.get("consumedService", "Unknown")),
                        resource_group=str(p.get("resourceGroup", "")),
                        cost=float(p.get("pretaxCost", 0)),
                        currency=str(p.get("billingCurrency", "USD")),
                        quantity=float(p.get("quantity", 0)),
                        unit=str(p.get("unitOfMeasure", "")),
                    )
                )
            url = data.get("nextLink")

        return records
