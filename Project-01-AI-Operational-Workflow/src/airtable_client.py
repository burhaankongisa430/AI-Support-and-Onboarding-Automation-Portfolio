"""
Airtable integration layer.

Writes triaged ticket records to an Airtable base via the REST API.
Expects an existing table named "Support Tickets" with the field schema
defined in README.md.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests


@dataclass
class TicketRecord:
    ticket_id: str
    customer_email: str
    subject: str
    body: str
    source: str
    urgency: str
    category: str
    sentiment: str
    key_issues: list[str]
    summary: str
    suggested_response: str
    received_at: str


class AirtableClient:
    BASE_URL = "https://api.airtable.com/v0"

    def __init__(self):
        self.api_key = os.environ["AIRTABLE_API_KEY"]
        self.base_id = os.environ["AIRTABLE_BASE_ID"]
        self.table_name = os.environ.get("AIRTABLE_TABLE_NAME", "Support Tickets")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def create_ticket(self, record: TicketRecord) -> dict:
        """Create a new record in Airtable and return the created row."""
        url = f"{self.BASE_URL}/{self.base_id}/{self.table_name}"
        payload = {
            "fields": {
                "Ticket ID": record.ticket_id,
                "Customer Email": record.customer_email,
                "Subject": record.subject,
                "Body": record.body,
                "Source": record.source,
                "Urgency": record.urgency,
                "Category": record.category,
                "Sentiment": record.sentiment,
                "Key Issues": "\n".join(f"• {issue}" for issue in record.key_issues),
                "Summary": record.summary,
                "Suggested Response": record.suggested_response,
                "Status": "Pending Review",
                "Received At": record.received_at,
            }
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def update_status(self, record_id: str, status: str) -> dict:
        """Update the Status field of an existing Airtable record."""
        url = f"{self.BASE_URL}/{self.base_id}/{self.table_name}/{record_id}"
        payload = {"fields": {"Status": status}}
        response = self.session.patch(url, json=payload)
        response.raise_for_status()
        return response.json()


def build_record(
    ticket_id: str,
    customer_email: str,
    subject: str,
    body: str,
    source: str,
    triage_result,
) -> TicketRecord:
    return TicketRecord(
        ticket_id=ticket_id,
        customer_email=customer_email,
        subject=subject,
        body=body,
        source=source,
        urgency=triage_result.urgency,
        category=triage_result.category,
        sentiment=triage_result.sentiment,
        key_issues=triage_result.key_issues,
        summary=triage_result.summary,
        suggested_response=triage_result.suggested_response,
        received_at=datetime.now(timezone.utc).isoformat(),
    )
