"""
Claude-powered welcome email generator.

Produces a personalised HTML welcome email for each new client based on
their company name, industry, plan, and stated use case.
"""

from __future__ import annotations

import json
import os

import anthropic

from pipeline import OnboardingPayload

SYSTEM_PROMPT = """You are a senior customer success writer at a B2B SaaS company.
Your task is to write a warm, professional, and genuinely personalised welcome email
for a new client who has just signed up.

Always respond with a single valid JSON object containing exactly two keys:
- "subject": the email subject line (concise, personalised, no clickbait)
- "body": the full email body as clean HTML (no <html>/<head>/<body> wrapper tags —
  just the inner content starting from a <p> tag)

Tone: warm but professional. Never use hollow phrases like "Excited to have you on board!"
Personalisation must feel specific — reference their industry, company size, or use case in a
meaningful way, not just by mentioning the company name.
""".strip()

USER_PROMPT_TEMPLATE = """Write a welcome email for the following new client:

- Name: {first_name} {last_name}
- Company: {company_name}
- Industry: {industry}
- Company size: {company_size} employees
- Plan: {plan}
- What they want to achieve: {use_case}
- Their account manager: {account_manager}

The email should:
1. Open with a specific, relevant observation about their industry or use case (not generic)
2. Briefly explain what to expect in the next 24–48 hours (account manager will reach out,
   onboarding session will be scheduled)
3. Give them one concrete action they can take right now (e.g. explore a specific feature
   relevant to their use case, or review the getting started guide)
4. Close warmly, signed from {account_manager}

Keep the email under 250 words. Respond with JSON only.
""".strip()


class WelcomeEmailGenerator:
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def generate(self, payload: OnboardingPayload) -> dict[str, str]:
        """Returns {"subject": str, "body": str} where body is inner HTML."""
        user_message = USER_PROMPT_TEMPLATE.format(
            first_name=payload.first_name,
            last_name=payload.last_name,
            company_name=payload.company_name,
            industry=payload.industry,
            company_size=payload.company_size,
            plan=payload.plan.title(),
            use_case=payload.use_case,
            account_manager=payload.account_manager,
        )

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw = message.content[0].text.strip()
        data = json.loads(raw)

        subject = data.get("subject", "Welcome to the platform")
        body = data.get("body", "")

        return {"subject": subject, "body": body}
