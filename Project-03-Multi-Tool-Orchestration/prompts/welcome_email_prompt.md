# Prompt Design — Personalised Welcome Email

## Overview

A two-message prompt: a `system` message that sets the writer's role and output contract,
and a `user` message that delivers the client profile and email requirements.

---

## System Prompt

```
You are a senior customer success writer at a B2B SaaS company.
Your task is to write a warm, professional, and genuinely personalised welcome email
for a new client who has just signed up.

Always respond with a single valid JSON object containing exactly two keys:
- "subject": the email subject line (concise, personalised, no clickbait)
- "body": the full email body as clean HTML (no <html>/<head>/<body> wrapper tags —
  just the inner content starting from a <p> tag)

Tone: warm but professional. Never use hollow phrases like "Excited to have you on board!"
Personalisation must feel specific — reference their industry, company size, or use case in a
meaningful way, not just by mentioning the company name.
```

**Design decisions:**
- "Senior customer success writer" produces more specific, less template-like copy than "email writer"
- Explicitly banning hollow phrases ("Excited to have you on board!") removes the most common AI email filler
- "Personalisation must feel specific" with examples of what "specific" means prevents the model from treating company name substitution as sufficient

---

## User Prompt Template

```
Write a welcome email for the following new client:

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
```

**Design decisions:**

| Choice | Reason |
|---|---|
| `use_case` field in the prompt | The single most powerful personalisation signal — allows Claude to reference *why* this client signed up, not just who they are |
| Numbered structural requirements | Prevents Claude from writing a generic intro → generic body → generic close; enforces a specific narrative arc |
| "one concrete action" constraint | Forces specificity; without this Claude produces vague "explore the platform" suggestions |
| Word count cap (250 words) | Welcome emails with high open-and-read rates are short; this prevents Claude from writing essays |
| JSON output with `body` as inner HTML | Allows SendGrid to receive clean HTML content without the pipeline having to strip wrapper tags |

---

## Output Schema

```json
{
  "subject": "Getting {company_name} started with {specific_thing}",
  "body": "<p>Hi {first_name},</p>\n<p>...</p>\n<p>Best,<br>{account_manager}</p>"
}
```

---

## Example Output (anonymised)

**Input:**
- Industry: Logistics
- Plan: Professional
- Use case: Automating delivery exception handling to reduce manual follow-up calls

**Output subject:**
```
Fewer exception calls, more deliveries on time — let's get started
```

**Output body (excerpt):**
```html
<p>Hi Jordan,</p>
<p>Logistics teams handling exception management manually face the same wall: by the time
a human reviews an exception, the window to proactively update the customer has already
closed. That's exactly the problem your team is solving with the Professional plan.</p>
<p>Here's what happens next: Sarah will reach out within 24 hours to schedule your onboarding
session, where you'll configure your first exception routing rules together...</p>
```

---

## Model

`claude-sonnet-4-6` — produces consistently specific, well-structured copy.
`claude-haiku-4-5-20251001` is viable for high-volume environments but produces
noticeably more generic openings on complex use cases.

---

## Token Usage (approximate)

| Component | Tokens |
|---|---|
| System prompt | ~120 |
| User prompt template | ~150 |
| Client profile fields | ~60–100 |
| Claude response (JSON + HTML) | ~400–600 |
| **Total per onboarding** | **~730–970** |
