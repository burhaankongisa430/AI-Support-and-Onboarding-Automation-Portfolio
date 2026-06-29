"""
Slack incoming-webhook notifier.

Posts a structured Block Kit message to the configured Slack channel
whenever a new client completes onboarding. The account manager sees
the client name, company, plan, and a direct link to the CRM record.
"""

from __future__ import annotations

import os

import requests

from pipeline import OnboardingPayload

PLAN_EMOJI = {
    "starter": ":seedling:",
    "professional": ":rocket:",
    "enterprise": ":crown:",
}


class SlackNotifier:
    def __init__(self):
        self.webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    def notify_account_manager(
        self,
        client_id: str,
        payload: OnboardingPayload,
        crm_record_id: str,
    ) -> None:
        """Post a Block Kit message to the #new-clients Slack channel."""
        airtable_base_id = os.environ.get("AIRTABLE_BASE_ID", "")
        crm_url = (
            f"https://airtable.com/{airtable_base_id}"
            if airtable_base_id else "#"
        )

        plan_key = payload.plan.lower()
        emoji = PLAN_EMOJI.get(plan_key, ":handshake:")

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji}  New client onboarded — {payload.company_name}",
                },
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Client:*\n{payload.first_name} {payload.last_name}"},
                    {"type": "mrkdwn", "text": f"*Company:*\n{payload.company_name}"},
                    {"type": "mrkdwn", "text": f"*Plan:*\n{payload.plan.title()}"},
                    {"type": "mrkdwn", "text": f"*Industry:*\n{payload.industry}"},
                    {"type": "mrkdwn", "text": f"*Company size:*\n{payload.company_size}"},
                    {"type": "mrkdwn", "text": f"*Account manager:*\n{payload.account_manager}"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Use case:*\n_{payload.use_case}_",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Client ID:* `{client_id}`   *CRM record:* `{crm_record_id}`",
                },
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Open in Airtable"},
                    "url": crm_url,
                    "action_id": "open_crm",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": (
                            f":white_check_mark: Welcome email sent to {payload.email}  "
                            f"|  :bell: {payload.account_manager} — please reach out within 24 h"
                        ),
                    }
                ],
            },
        ]

        resp = requests.post(self.webhook_url, json={"blocks": blocks})
        resp.raise_for_status()
