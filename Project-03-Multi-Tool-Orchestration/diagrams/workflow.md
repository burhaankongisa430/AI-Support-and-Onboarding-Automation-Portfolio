# Workflow Diagram — Automated Client Onboarding Pipeline

## End-to-End System Flow

```mermaid
flowchart TD
    A([New client\ncompletes sign-up form]) -->|Form submission| B

    subgraph TRIGGER ["Trigger Layer (Zapier / Make)"]
        B[Google Form / Typeform\nwebhook trigger]
        C[POST /webhook/onboard\nFormatted JSON payload]
        B --> C
    end

    subgraph SERVER ["Pipeline Server (Flask · Python)"]
        D[Validate payload\n9 required fields]
        E[Assign Client ID\nCLT-XXXXXX]
        D --> E
    end

    subgraph STEP1 ["Step 1 — CRM Record Creation"]
        F[Airtable REST API\nCreate client record\nStatus = Onboarding]
    end

    subgraph STEP2 ["Step 2 — Email Generation"]
        G[Claude Sonnet API\nPersonalised welcome email\nSubject + HTML body]
    end

    subgraph STEP3 ["Step 3 — Email Delivery"]
        H[SendGrid REST API\nDeliver HTML email\nto client inbox]
    end

    subgraph STEP4 ["Step 4 — AM Notification"]
        I[Slack Incoming Webhook\nBlock Kit message\nto #new-clients channel]
    end

    subgraph STEP5 ["Step 5 — CRM Status Update"]
        J[Airtable REST API\nWrite delivery timestamps\nWelcome Email Sent = true]
    end

    subgraph RESPONSE ["Pipeline Trace Response"]
        K[JSON trace:\nrun_id · client_id · outcome\nper-step status + duration_ms]
    end

    C --> D
    E --> F
    F -->|crm_record_id| G
    G -->|subject + HTML body| H
    H --> I
    I --> J
    J --> K

    F -.->|failure halts pipeline| K
    G -.->|failure halts pipeline| K
    H -.->|failure halts pipeline| K
    I -.->|failure = partial outcome\npipeline continues| J
    J -.->|failure = partial outcome| K

    style TRIGGER fill:#e3f2fd,stroke:#1565C0
    style SERVER fill:#fff8e1,stroke:#E65100
    style STEP1 fill:#e8f5e9,stroke:#2E7D32
    style STEP2 fill:#f3e5f5,stroke:#6A1B9A
    style STEP3 fill:#e0f7fa,stroke:#006064
    style STEP4 fill:#fff3e0,stroke:#BF360C
    style STEP5 fill:#e8f5e9,stroke:#2E7D32
    style RESPONSE fill:#fce4ec,stroke:#880E4F
```

---

## System Connections Map

```mermaid
graph LR
    FORM[Google Form\nor Typeform]
    ZAPIER[Zapier / Make\norchestration]
    SERVER[Pipeline Server\nFlask · Python]
    CLAUDE[Claude API\nAnthropic]
    AIRTABLE[(Airtable\nCRM)]
    SENDGRID[SendGrid\nEmail delivery]
    SLACK[Slack\n#new-clients]
    CLIENT([Client inbox])
    AM([Account manager])

    FORM -->|submission| ZAPIER
    ZAPIER -->|POST webhook| SERVER
    SERVER -->|create record| AIRTABLE
    SERVER -->|generate email| CLAUDE
    CLAUDE -->|subject + HTML| SERVER
    SERVER -->|send email| SENDGRID
    SENDGRID -->|delivered| CLIENT
    SERVER -->|Block Kit message| SLACK
    SLACK -->|notification| AM
    SERVER -->|update timestamps| AIRTABLE
```

---

## Pipeline Step Detail

| Step | System | Critical | On failure |
|---|---|---|---|
| 1. CRM record creation | Airtable | Yes | Pipeline halts; 502 returned |
| 2. Email generation | Claude API | Yes | Pipeline halts; 502 returned |
| 3. Email delivery | SendGrid | Yes | Pipeline halts; 502 returned |
| 4. AM notification | Slack | No | Logged; outcome = "partial"; pipeline continues |
| 5. CRM status update | Airtable | No | Logged; outcome = "partial" |

---

## Pipeline Trace Response (sample)

```json
{
  "run_id": "RUN-4A3B2C1D",
  "client_id": "CLT-F7E6D5",
  "started_at": "2024-11-14T09:32:01.441Z",
  "completed_at": "2024-11-14T09:32:03.887Z",
  "total_duration_ms": 2446,
  "outcome": "success",
  "steps": [
    { "step": "crm_create",      "status": "success", "at": "2024-11-14T09:32:01.443Z", "duration_ms": 341, "crm_record_id": "recXXXXXXXXXXXXXX" },
    { "step": "email_generate",  "status": "success", "at": "2024-11-14T09:32:01.785Z", "duration_ms": 1204, "subject": "Fewer exception calls, more deliveries on time — let's get started" },
    { "step": "email_send",      "status": "success", "at": "2024-11-14T09:32:02.990Z", "duration_ms": 287, "message_id": "d3b07384d113edec49eaa6238ad5ff00" },
    { "step": "slack_notify",    "status": "success", "at": "2024-11-14T09:32:03.278Z", "duration_ms": 412 },
    { "step": "crm_update",      "status": "success", "at": "2024-11-14T09:32:03.691Z", "duration_ms": 196 }
  ]
}
```

---

## Zapier Scenario Map

| Step | Module | Configuration |
|---|---|---|
| Trigger | Google Forms — New Response | Watch the onboarding sign-up form |
| Action 1 | Webhooks by Zapier — POST | `https://your-server/webhook/onboard` with all form fields mapped to JSON |
| Action 2 | Filter — Only continue if | `outcome` = "success" or "partial" (skip on 502) |
| Action 3 (optional) | Delay — Wait | 24 hours |
| Action 4 (optional) | Slack — Send message | Reminder to AM: "Have you reached out to {{company_name}} yet?" |

For Make (Integromat): use the HTTP module for the webhook POST; the trace JSON response
maps directly into downstream modules via the `steps[*].status` path.
