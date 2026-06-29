"""
Airtable CRM client for the client onboarding pipeline.

Manages a "Clients" table that stores every new client record
with full onboarding status tracking.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import requests

from pipeline import OnboardingPayload


class AirtableCRMClient:
    BASE_URL = "https://api.airtable.com/v0"

    def __init__(self):
        self.api_key = os.environ["AIRTABLE_API_KEY"]
        self.base_id = os.environ["AIRTABLE_BASE_ID"]
        self.table_name = os.environ.get("AIRTABLE_CLIENTS_TABLE", "Clients")
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def _url(self) -> str:
        return f"{self.BASE_URL}/{self.base_id}/{self.table_name}"

    def create_client(self, client_id: str, payload: OnboardingPayload) -> dict:
        """Create a new client record. Returns the raw Airtable response."""
        body = {
            "fields": {
                "Client ID": client_id,
                "First Name": payload.first_name,
                "Last Name": payload.last_name,
                "Email": payload.email,
                "Company": payload.company_name,
                "Industry": payload.industry,
                "Company Size": payload.company_size,
                "Plan": payload.plan.title(),
                "Account Manager": payload.account_manager,
                "Use Case": payload.use_case,
                "Source": payload.source,
                "Status": "Onboarding",
                "Welcome Email Sent": False,
                "AM Notified": False,
                "Onboarded At": datetime.now(timezone.utc).isoformat(),
            }
        }
        resp = self._session.post(self._url(), json=body)
        resp.raise_for_status()
        return resp.json()

    def update_onboarding_status(
        self,
        record_id: str,
        welcome_email_sent: bool,
        am_notified: bool,
    ) -> dict:
        """Update delivery flags after pipeline completes."""
        now = datetime.now(timezone.utc).isoformat()
        fields: dict = {
            "Welcome Email Sent": welcome_email_sent,
            "AM Notified": am_notified,
        }
        if welcome_email_sent:
            fields["Welcome Email Sent At"] = now
        if am_notified:
            fields["AM Notified At"] = now

        url = f"{self._url()}/{record_id}"
        resp = self._session.patch(url, json={"fields": fields})
        resp.raise_for_status()
        return resp.json()
