# Architecture — AI-Powered Support Ticket Triage System

## System Flow Diagram

```mermaid
flowchart TD
    A([Customer]) -->|Submits ticket| B

    subgraph INPUT ["Input Layer"]
        B[Google Form / Zapier Webhook / Email]
    end

    subgraph SERVER ["Webhook Server (Flask · Python)"]
        C[POST /webhook/ticket\nField validation\nTicket ID generation]
    end

    subgraph AI ["AI Triage Layer (Anthropic · Claude Sonnet)"]
        D[System prompt\nRole + JSON contract]
        E[User prompt\nSubject + Body + field schema]
        F[Claude response\nJSON: urgency · category · sentiment\nkey issues · summary · draft reply]
        D --> E --> F
    end

    subgraph CRM ["Data Layer (Airtable REST API)"]
        G[Support Tickets table\nRecord created · Status = Pending Review]
    end

    subgraph AGENT ["Agent Notification (optional extension)"]
        H[Slack / Teams alert\nfor Critical & High tickets]
    end

    B -->|JSON payload\nemail · subject · body · source| C
    C -->|subject + body| AI
    F -->|structured result| C
    C -->|enriched record| G
    G -->|webhook trigger| H

    style INPUT fill:#e8f4fd,stroke:#2196F3
    style SERVER fill:#fff8e1,stroke:#FF9800
    style AI fill:#f3e5f5,stroke:#9C27B0
    style CRM fill:#e8f5e9,stroke:#4CAF50
    style AGENT fill:#fce4ec,stroke:#E91E63
```

---

## Component Responsibilities

| Component | Technology | Responsibility |
|---|---|---|
| **Input trigger** | Google Form / Zapier / Make / custom form | Captures customer ticket and forwards to webhook |
| **Webhook server** | Python · Flask | Validates payload, assigns ticket ID, orchestrates flow |
| **AI triage engine** | Anthropic Claude Sonnet via Python SDK | Classifies urgency/category/sentiment, extracts issues, drafts reply |
| **Airtable client** | Airtable REST API | Persists enriched ticket record for agent review |
| **Notification (opt.)** | Slack API / Teams webhook | Alerts on-call agent for Critical or High urgency tickets |

---

## Data Flow Detail

```
1. Customer submits form/email
        ↓
2. Zapier / Make triggers POST /webhook/ticket
   {email, subject, body, source}
        ↓
3. Flask validates fields, generates TKT-XXXXXXXX
        ↓
4. Claude API call:
   - System: role + JSON-only contract
   - User: ticket content + field constraints
   → Returns {urgency, category, sentiment, key_issues, summary, suggested_response}
        ↓
5. Airtable REST POST: creates record in "Support Tickets" table
   Status = "Pending Review"
        ↓
6. HTTP 201 response returned to Zapier/Make
   → downstream steps can branch on urgency field
        ↓
7. (Optional) Zapier filter: if urgency = Critical or High
   → Slack message to #support-alerts channel
```

---

## Airtable Table Schema

| Field | Type | Description |
|---|---|---|
| Ticket ID | Single line text | Auto-generated (e.g. TKT-A3F2C1B8) |
| Customer Email | Email | From submission |
| Subject | Single line text | Original subject |
| Body | Long text | Original ticket body |
| Source | Single select | form · email · zapier · webhook |
| Urgency | Single select | Critical · High · Medium · Low |
| Category | Single select | Technical · Billing · Feature Request · Bug Report · General |
| Sentiment | Single select | Positive · Neutral · Negative · Frustrated |
| Key Issues | Long text | Bullet list of extracted problems |
| Summary | Single line text | One-sentence agent-readable summary |
| Suggested Response | Long text | AI-drafted reply ready to send |
| Status | Single select | Pending Review · In Progress · Resolved |
| Received At | Date/time | ISO 8601 UTC timestamp |

---

## Zapier Integration Map

```
Trigger  → Google Form submission (or Typeform / Jotform)
Action 1 → Webhooks by Zapier: POST to /webhook/ticket
Action 2 → Filter: only continue if urgency = Critical or High  (optional branch)
Action 3 → Slack: send message to #support-alerts               (optional branch)
```
