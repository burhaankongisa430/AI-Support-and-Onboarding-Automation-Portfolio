"""
Claude-powered triage engine for incoming support tickets.

Classifies urgency, extracts key details, and drafts a suggested response
using the Anthropic Messages API.
"""

import json
import os
from dataclasses import dataclass

import anthropic

URGENCY_LEVELS = ("Critical", "High", "Medium", "Low")
CATEGORIES = ("Technical", "Billing", "Feature Request", "Bug Report", "General")
SENTIMENTS = ("Positive", "Neutral", "Negative", "Frustrated")

SYSTEM_PROMPT = """You are an expert support operations analyst embedded in a business workflow.
Your job is to triage incoming customer support tickets and produce a structured analysis that
allows a support agent to respond quickly and effectively.

Always respond with a single valid JSON object — no markdown fencing, no prose outside the JSON.
""".strip()

USER_PROMPT_TEMPLATE = """Analyse the following support ticket and return a JSON object with
exactly these keys:

- urgency        : one of {urgency_levels}
- category       : one of {categories}
- sentiment      : one of {sentiments}
- key_issues     : a list of 2–4 concise bullet strings describing the core problems
- summary        : one sentence (≤ 30 words) that an agent can read at a glance
- suggested_response : a professional, empathetic reply draft (150–200 words) ready to send
                       to the customer. Do NOT include a subject line.

---
TICKET SUBJECT: {subject}

TICKET BODY:
{body}
---

Respond with JSON only.
""".strip()


@dataclass
class TriageResult:
    urgency: str
    category: str
    sentiment: str
    key_issues: list[str]
    summary: str
    suggested_response: str

    def to_dict(self) -> dict:
        return {
            "urgency": self.urgency,
            "category": self.category,
            "sentiment": self.sentiment,
            "key_issues": self.key_issues,
            "summary": self.summary,
            "suggested_response": self.suggested_response,
        }


class TicketTriageEngine:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def triage(self, subject: str, body: str) -> TriageResult:
        """Send a ticket to Claude and parse the structured triage response."""
        user_message = USER_PROMPT_TEMPLATE.format(
            urgency_levels=", ".join(URGENCY_LEVELS),
            categories=", ".join(CATEGORIES),
            sentiments=", ".join(SENTIMENTS),
            subject=subject,
            body=body,
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text.strip()
        data = json.loads(raw)
        return self._validate_and_build(data)

    def _validate_and_build(self, data: dict) -> TriageResult:
        urgency = data.get("urgency", "Medium")
        if urgency not in URGENCY_LEVELS:
            urgency = "Medium"

        category = data.get("category", "General")
        if category not in CATEGORIES:
            category = "General"

        sentiment = data.get("sentiment", "Neutral")
        if sentiment not in SENTIMENTS:
            sentiment = "Neutral"

        key_issues = data.get("key_issues", [])
        if not isinstance(key_issues, list):
            key_issues = [str(key_issues)]

        return TriageResult(
            urgency=urgency,
            category=category,
            sentiment=sentiment,
            key_issues=key_issues,
            summary=data.get("summary", ""),
            suggested_response=data.get("suggested_response", ""),
        )
