"""
Email delivery via SendGrid REST API.

Wraps the HTTP call so the rest of the pipeline has no dependency on
the SendGrid SDK — just a clean send() interface.
"""

from __future__ import annotations

import os

import requests

FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@example.com")
FROM_NAME = os.environ.get("FROM_NAME", "The Team")


class SendGridEmailSender:
    API_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self):
        self.api_key = os.environ["SENDGRID_API_KEY"]

    def send(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        body_html: str,
    ) -> str:
        """Send an HTML email and return the SendGrid message ID."""
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to_email, "name": to_name}],
                    "subject": subject,
                }
            ],
            "from": {"email": FROM_EMAIL, "name": FROM_NAME},
            "content": [{"type": "text/html", "value": body_html}],
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        resp = requests.post(self.API_URL, json=payload, headers=headers)
        resp.raise_for_status()

        # SendGrid returns the message ID in the X-Message-Id response header
        return resp.headers.get("X-Message-Id", "unknown")
