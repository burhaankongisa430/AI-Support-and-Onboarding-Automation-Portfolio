# Project 3 — Multi-Tool Automation Orchestration

---

## Business Problem

When a new client signs up, teams face a race against first impressions: the faster a
personalised welcome reaches the client and the account manager is alerted, the higher
the activation rate. Manual onboarding (copy-paste welcome emails, manual CRM entry,
Slack pings) introduces delays, inconsistency, and data gaps that compound over time.

This project orchestrates five systems into a single automated pipeline that completes
a full onboarding sequence in under 3 seconds, with zero manual steps.

---

## What It Does

A new client submits a sign-up form. Within seconds:

1. **CRM record created** in Airtable with full client profile and `Status: Onboarding`
2. **Personalised welcome email generated** by Claude, referencing the client's specific industry and use case, not a template
3. **Welcome email delivered** to the client via SendGrid
4. **Account manager alerted** in Slack with a structured Block Kit message and a direct CRM link
5. **CRM updated** with delivery timestamps and status flags

Every pipeline run returns a full trace (step-by-step status, timing, and outcome) so failures are visible and diagnosable immediately.

---

## Systems Connected

| System | Role | Tool |
|---|---|---|
| Google Form / Typeform | Client intake trigger | Zapier webhook |
| Flask (Python) | Pipeline orchestrator | Custom server |
| Airtable | CRM — client records | REST API |
| Claude (Anthropic) | Welcome email generation | Python SDK |
| SendGrid | Email delivery | REST API |
| Slack | Account manager notification | Incoming webhook |

**Six systems. One webhook call. Under 3 seconds end-to-end.**

---

## Architecture

See [diagrams/workflow.md](diagrams/workflow.md) for the full Mermaid flow diagram and system connections map.

```
Google Form → Zapier → POST /webhook/onboard (Flask)
    → Airtable: create record
    → Claude: generate personalised email
    → SendGrid: deliver email
    → Slack: notify account manager
    → Airtable: update timestamps
    → Pipeline trace returned (JSON)
```

---

## Repository Structure

```
Project-03-Multi-Tool-Orchestration/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── main.py              # Flask entry point — routing and validation
│   ├── pipeline.py          # Orchestration engine — step runner + trace builder
│   ├── crm.py               # Airtable CRM client
│   ├── email_generator.py   # Claude welcome email generation
│   ├── email_sender.py      # SendGrid delivery
│   └── slack_notifier.py    # Slack Block Kit notification
├── prompts/
│   └── welcome_email_prompt.md   # Prompt design + personalisation rationale
├── diagrams/
│   └── workflow.md               # Mermaid end-to-end + system connections map
├── tests/
│   └── test_pipeline.py          # 18 unit tests (no API keys required)
└── sample_data/
    ├── sample_onboarding_input.json    # Example POST body
    ├── sample_pipeline_trace.json      # Example pipeline trace response
    └── sample_email_output.html        # Example Claude-generated welcome email
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY, AIRTABLE_API_KEY, AIRTABLE_BASE_ID,
#          SENDGRID_API_KEY, FROM_EMAIL, SLACK_WEBHOOK_URL
```

### 3. Create the Airtable "Clients" table

Fields required: Client ID, First Name, Last Name, Email, Company, Industry,
Company Size, Plan, Account Manager, Use Case, Source, Status, Welcome Email Sent,
Welcome Email Sent At, AM Notified, AM Notified At, Onboarded At.

### 4. Run the server

```bash
python src/main.py
# Starts on http://localhost:5001
```

### 5. Trigger a test onboarding

```bash
curl -X POST http://localhost:5001/webhook/onboard \
  -H "Content-Type: application/json" \
  -d @sample_data/sample_onboarding_input.json
```

Expected response (HTTP 201):
```json
{
  "run_id": "RUN-4A3B2C1D",
  "client_id": "CLT-F7E6D5",
  "outcome": "success",
  "total_duration_ms": 2446,
  "steps": [...]
}
```

---

## Running Tests

```bash
pytest tests/test_pipeline.py -v
```

18 tests covering the happy path, all three critical failure modes, both
non-critical failure modes, and the Flask endpoint validation. No API keys
or external services required.

---

## Pipeline Outcomes

The pipeline returns one of three outcomes:

| Outcome | Meaning | HTTP status |
|---|---|---|
| `success` | All 5 steps completed | 201 |
| `partial` | Critical steps completed; Slack or CRM update failed | 207 |
| `failed` | A critical step failed; pipeline halted | 502 |

This design means Zapier/Make can branch on the `outcome` field to handle
partial completions differently from full failures — for example, retrying
just the Slack notification without re-triggering the email.

---

## Trade-offs

| Decision | What was gained | What was given up |
|---|---|---|
| Sequential pipeline over parallel steps | Simple trace, easy to debug, steps can depend on previous results (e.g. CRM ID needed for Slack message) | Slower than running independent steps in parallel; total time = sum of all step times |
| Critical vs non-critical step distinction | Slack failure never loses a client record or welcome email | Requires explicit classification of every step — wrong classification has consequences |
| Returning a full pipeline trace on every call | Immediate observability; Zapier can branch on per-step outcomes | Larger response payload; not needed for simple use cases |
| Claude for email generation over a fixed template | Every email is specific to the client's industry and use case; higher activation signal | Adds ~1.2 s and API cost per onboarding; template would be instant and free |
| SendGrid over SMTP | Reliable delivery, bounce tracking, open rates via SendGrid dashboard | Vendor dependency; SMTP is universally available with no setup |

---

## What Was Learned

**Pipeline observability is worth the upfront cost.** The step trace (timing, status, detail on failure) added ~30 lines of code to `pipeline.py` and saved hours the first time a step failed silently in testing. Without it, a Slack webhook timeout looked identical to a SendGrid failure from the outside.

**Prompt specificity drives personalisation quality.** The first prompt version produced emails that mentioned the company name and industry but felt templated. Adding the `use_case` field and the instruction "open with a specific, relevant observation about their industry or use case (not generic)" shifted the output from substitution to genuine personalisation. The difference is visible in [sample_data/sample_email_output.html](sample_data/sample_email_output.html).

**Non-critical step failure handling changes the product conversation.** Distinguishing Slack notification as non-critical (vs critical) was a design decision, not a default. If Slack fails and the account manager isn't notified, the client still receives a welcome email — the worst case is a delayed first call, not a missing client record. Making that call explicit in code forces the architect to think through the failure mode before it happens in production.
