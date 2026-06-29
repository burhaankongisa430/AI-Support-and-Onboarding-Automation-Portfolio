# Prompt Design — Ticket Triage

## Overview

Two-message prompt: a `system` message that sets the role and output contract,
and a `user` message that delivers the ticket and field schema.

---

## System Prompt

```
You are an expert support operations analyst embedded in a business workflow.
Your job is to triage incoming customer support tickets and produce a structured analysis that
allows a support agent to respond quickly and effectively.

Always respond with a single valid JSON object — no markdown fencing, no prose outside the JSON.
```

**Design decisions:**
- "embedded in a business workflow" signals this is a functional component, not a conversational chatbot, which consistently reduces conversational filler in the output.
- The JSON-only constraint is explicit and repeated ("no markdown fencing, no prose outside the JSON") because Claude will occasionally wrap JSON in code fences when the instruction is vague.

---

## User Prompt Template

```
Analyse the following support ticket and return a JSON object with
exactly these keys:

- urgency        : one of Critical, High, Medium, Low
- category       : one of Technical, Billing, Feature Request, Bug Report, General
- sentiment      : one of Positive, Neutral, Negative, Frustrated
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
```

**Design decisions:**

| Choice | Reason |
|---|---|
| Enumerated field values in the prompt | Constrains classification to a known set; downstream code can validate without LLM guardrails |
| `key_issues` as a list, not a string | Preserves machine-readable structure so each issue can be rendered as a Airtable bullet |
| Word-count bounds on `summary` and `suggested_response` | Prevents runaway verbosity; agents need scannable output, not essays |
| "Do NOT include a subject line" in the response draft | Prevents Claude from adding "Subject: Re: …" which agents would need to strip manually |
| Ticket subject kept separate from body | Allows Claude to weigh subject-line hyperbole (e.g. "URGENT!!") independently from body tone |

---

## Output Schema

```json
{
  "urgency": "High",
  "category": "Technical",
  "sentiment": "Frustrated",
  "key_issues": [
    "Login button unresponsive on mobile Chrome since the 14 June update",
    "Customer has been locked out for 48 hours",
    "Password reset email not arriving despite multiple requests"
  ],
  "summary": "Mobile login is broken for customer since last update; password reset is also failing.",
  "suggested_response": "Thank you for reaching out, and I sincerely apologise for the disruption this has caused. ..."
}
```

---

## Model

`claude-sonnet-4-6` — chosen for its balance of reasoning quality and cost at scale.
For very high-volume environments, `claude-haiku-4-5-20251001` is a viable drop-in
that reduces per-ticket API cost at a small accuracy trade-off on nuanced sentiment.

---

## Token Usage (approximate)

| Component | Tokens |
|---|---|
| System prompt | ~55 |
| User prompt template | ~130 |
| Average ticket body | ~100–200 |
| Claude response (JSON) | ~300–400 |
| **Total per ticket** | **~585–785** |

At `claude-sonnet-4-6` pricing this is well under $0.01 per ticket, making it
economically viable at thousands of tickets per day.
