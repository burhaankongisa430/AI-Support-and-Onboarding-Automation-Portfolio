# Project 1 — AI-Powered Support Ticket Triage System

**Portfolio project for the AI Automation Architect role**

---

## Business Problem

Support teams receive tickets in an unstructured mix of urgencies and topics.
Manual triage is slow, inconsistent, and keeps agents from spending time on actual resolution.
High-urgency tickets can sit unread for hours simply because they arrived between busy periods.

This project embeds Claude AI directly into the ticket intake workflow so that every ticket is
classified, summarised, and given a draft response **before a human agent ever sees it** — turning
a reactive queue into a prioritised, pre-enriched workbench.

---

## What It Does

```
Customer submits ticket (form / email / webhook)
        ↓
Webhook server receives and validates the payload
        ↓
Claude API classifies urgency, category, and sentiment
extracts key issues, writes a one-sentence summary,
and drafts a professional response
        ↓
Enriched record is created in Airtable (Status: Pending Review)
        ↓
(Optional) Slack alert fires for Critical / High tickets
```

**Output per ticket:**

| Field | Example |
|---|---|
| Urgency | Critical / High / Medium / Low |
| Category | Technical / Billing / Bug Report / Feature Request / General |
| Sentiment | Frustrated / Negative / Neutral / Positive |
| Key Issues | Bullet list of 2–4 extracted problems |
| Summary | "Customer locked out since update; password reset failing" |
| Suggested Response | 150–200 word professional draft, ready to send |

---

## Architecture

See [diagrams/architecture.md](diagrams/architecture.md) for the full flow diagram and Airtable schema.

**High-level:**

```
[Google Form / Zapier Trigger]
        → POST /webhook/ticket  (Flask · Python)
        → Claude Sonnet API     (Anthropic SDK)
        → Airtable REST API     (Support Tickets table)
        → (Optional) Slack API  (Critical/High alert)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI | Anthropic Claude (`claude-sonnet-4-6`) |
| Webhook server | Python · Flask |
| Orchestration | Zapier or Make (no-code trigger layer) |
| CRM / data store | Airtable |
| Notifications | Slack (optional Zapier step) |

---

## Repository Structure

```
Project-01-AI-Operational-Workflow/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py              # Flask webhook server + routing
│   ├── triage.py            # Claude API triage engine
│   └── airtable_client.py   # Airtable REST integration
├── prompts/
│   └── triage_prompt.md     # Prompt design rationale + schema
├── tests/
│   ├── test_triage.py       # Unit + endpoint tests (no API key needed)
│   └── sample_tickets.json  # Four representative test tickets
└── diagrams/
    └── architecture.md      # Mermaid flow diagram + component table
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd Project-01-AI-Operational-Workflow
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required values:
- `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com)
- `AIRTABLE_API_KEY` — personal access token from [airtable.com/create/tokens](https://airtable.com/create/tokens)
- `AIRTABLE_BASE_ID` — found in your Airtable base API docs

### 3. Create the Airtable table

Create a base called **Support Operations** with a table called **Support Tickets** using the
schema in [diagrams/architecture.md](diagrams/architecture.md#airtable-table-schema).

### 4. Run the server

```bash
python src/main.py
```

Server starts on `http://localhost:5000`.

### 5. Send a test ticket

```bash
curl -X POST http://localhost:5000/webhook/ticket \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "subject": "Cannot log in since the update",
    "body": "Hi, I have been locked out of my account since yesterday. The password reset email is not arriving. I have an important meeting in 2 hours. Please help urgently.",
    "source": "form"
  }'
```

Expected response (HTTP 201):
```json
{
  "ticket_id": "TKT-A3F2C1B8",
  "airtable_record_id": "recXXXXXXXXXXXXXX",
  "urgency": "Critical",
  "category": "Technical",
  "sentiment": "Frustrated",
  "summary": "Customer locked out since the latest update with password reset not working."
}
```

---

## Running Tests

No API key required for unit tests — the Anthropic client is mocked.

```bash
pytest tests/test_triage.py -v
```

---

## Zapier Integration

1. **Trigger:** Google Form submission (or Typeform, Jotform)
2. **Action 1:** Webhooks by Zapier → POST to `https://your-server/webhook/ticket`
3. **Action 2 (optional):** Filter → only continue if `urgency` = Critical or High
4. **Action 3 (optional):** Slack → send message to `#support-alerts`

For Make (Integromat): use the HTTP module for the webhook call; the response JSON can
be mapped directly into subsequent modules.

---

## Prompt Design

See [prompts/triage_prompt.md](prompts/triage_prompt.md) for:
- Full system and user prompt text
- Design rationale for each choice
- Token usage estimate (~600–800 tokens per ticket)
- Model selection reasoning

---

## Outcome

- Every ticket arrives pre-classified, pre-summarised, and with a draft response
- Agents skip triage and go straight to resolution
- Urgency routing (via Zapier filter) ensures Critical tickets trigger an immediate Slack alert
- Average triage time drops from 3–5 minutes per ticket to under 5 seconds end-to-end

---

## Trade-offs

| Decision | What was gained | What was given up |
|---|---|---|
| Claude Sonnet over Haiku | Higher accuracy on nuanced sentiment and multi-issue tickets | ~4–5× higher cost per ticket at scale |
| Single synchronous API call per ticket | Simple linear flow, easy to debug and trace | If Claude is slow or unavailable, the webhook response is delayed; no retry or queue |
| Airtable as the data store | Zero infrastructure to manage, fast to set up, visual for non-technical stakeholders | Not suitable beyond ~100k records; no relational integrity between tickets and customers |
| Enumerated field values in the prompt | Keeps classification deterministic and easy to validate in code | Rigid — adding a new category means updating the prompt, validation list, and Airtable field simultaneously |
| Flask over a serverless function | Easier local development and testing | Requires a persistent host (e.g. Railway, Render); a Lambda/Cloud Function would be more operationally lean in production |
| Zapier as the orchestration layer | Non-technical stakeholders can view and modify the trigger without touching code | Zapier adds latency (~1–3 s) and a per-task cost; for high volume, a direct webhook from the form is faster |

---

## What Can Be Improved (Lessons Learned)

**1. Add a retry queue for API failures**
The current implementation returns a 502 immediately if the Claude call fails. In production, transient failures should push the ticket to a dead-letter queue (e.g. a Redis list or an SQS queue) and retry with exponential backoff, rather than losing the ticket silently.

**2. Decouple the AI call from the HTTP response**
Right now the webhook waits for Claude to respond before returning to Zapier. Zapier has a 30-second timeout, which is usually fine, but under load this becomes fragile. A better pattern is to accept the ticket, return 202 immediately, and process the triage asynchronously (e.g. Celery, a background thread, or a cloud task queue).

**3. Human-in-the-loop for low-confidence classifications**
The model does not expose a confidence score for its classification. In edge cases — ambiguous tickets, very short bodies, non-English text — the triage result can be unreliable. A future version should ask Claude to include a `confidence` field and route low-confidence tickets to a human review queue rather than directly to agents.

**4. Webhook authentication**
The current endpoint accepts any POST request. In production, every Zapier or Make webhook should include a shared secret in a header (`X-Webhook-Secret`) that the server validates before processing — otherwise the intake endpoint is open to spoofed tickets.

**5. Prompt versioning**
The triage prompt is embedded in source code with no versioning. If the prompt changes, there is no way to know which prompt produced a given historical ticket. A better approach is to store a `prompt_version` field on every Airtable record so classification drift can be audited and traced back to a specific prompt change.

**6. Observability**
There is currently no structured logging beyond `print`-style log lines. A production deployment should emit structured JSON logs (e.g. via `structlog`) with `ticket_id`, `urgency`, `latency_ms`, and `model` on every request, feeding into a dashboard that tracks classification distribution and API latency over time.
