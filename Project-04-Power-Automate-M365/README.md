# Project 4 — Power Automate + Microsoft 365 Integration

---

## Business Problem

Compliance teams in mid-to-large organisations maintain dozens of weekly checks across areas like data privacy, IT security, financial controls, and HR. Manually compiling these into a readable report — pulling from a SharePoint list, writing a summary, formatting an email, notifying the team — takes 2–4 hours every Monday and produces inconsistent output depending on who wrote it.

This project automates the entire cycle: data retrieval, validation, AI-powered executive summary, and multi-channel distribution; all triggered automatically every Monday morning, with full audit logging and error handling built in.

---

## What It Does

Every Monday at 07:00 EST, without any manual action:

1. **Retrieves** all compliance check items updated in the last 7 days from SharePoint
2. **Validates** required fields (Owner, DueDate, RiskLevel) — flags data quality gaps
3. **Filters** to items that require attention (non-compliant, open findings, or missing fields)
4. **Generates** an AI-powered executive summary via Claude, including risk assessment, key findings, and recommended actions with specific owners
5. **Composes** a full HTML report with stats table and AI sections
6. **Logs** the run to an audit trail before distribution begins
7. **Distributes** via Outlook email to the compliance distribution list
8. **Posts** a summary card to the Microsoft Teams compliance channel
9. **Handles failures** with a Catch scope: logs errors to audit trail, sends failure alert email

---

## Systems Used

| System | Role |
|---|---|
| Power Automate (Premium) | Flow orchestration — all steps |
| SharePoint | Source data (Compliance Checks list) + audit trail (Report Audit Log) |
| Azure Functions (Python) | Stateless AI summary endpoint |
| Claude Sonnet (Anthropic) | Executive summary generation |
| Office 365 Outlook | HTML report email distribution |
| Microsoft Teams | Summary card to compliance channel |

---

## Repository Structure

```
Project-04-Power-Automate-M365/
├── README.md
├── governance.md                          # Error handling, credential management, monitoring
├── flow/
│   ├── compliance-report-flow.json        # Exported Power Automate flow definition
│   └── flow-description.md               # Step-by-step flow documentation with design rationale
├── azure-function/
│   ├── function_app.py                    # Python v2 Azure Function — AI summary endpoint
│   ├── requirements.txt                   # anthropic, azure-functions
│   ├── host.json                          # Function app configuration
│   └── local.settings.json.example       # Local dev environment template
├── diagrams/
│   └── architecture.md                   # Mermaid system flow + component map + data flow
├── sharepoint/
│   └── list-schema.md                    # Column schemas for both SharePoint lists
└── sample_data/
    ├── sample-compliance-data.json        # Sample payload sent to the Azure Function
    └── sample-ai-summary.json            # Sample Claude response embedded in the report
```

---

## How to Import and Run the Flow

### Prerequisites
- Power Automate Premium licence (required for HTTP action)
- SharePoint site with the two lists configured per [sharepoint/list-schema.md](sharepoint/list-schema.md)
- Azure Function deployed (see below)
- Service account with appropriate M365 permissions

### 1. Deploy the Azure Function

```bash
cd azure-function
pip install -r requirements.txt

# Set the Anthropic API key as an App Setting in the Azure portal
# (never in local.settings.json committed to source control)

func azure functionapp publish <your-function-app-name>
```

### 2. Import the Power Automate flow

1. Go to **Power Automate → My Flows → Import → Import Package**
2. Select `flow/compliance-report-flow.json`
3. Update all connection references (SharePoint, Outlook, Teams)
4. Update flow parameters:
   - `SharePointSiteUrl` — your compliance site URL
   - `AISummaryFunctionUrl` — your deployed Azure Function URL
   - `AISummaryFunctionKey` — the function-level key from Azure portal
   - `DistributionEmailList` — semicolon-separated email list
   - `TeamsChannelId` / `TeamsGroupId` — from Teams channel settings
5. Save and enable the flow

### 3. Test the flow

Run the flow manually from Power Automate → [Flow name] → Run. Check:
- SharePoint Audit Log for a new record
- Inbox for the HTML report email
- Teams compliance channel for the summary card
- Azure Function logs (Application Insights) for the AI generation call

---

## Error Handling Summary

The flow uses a **Try/Catch scope pattern** — the standard Power Automate equivalent of a try/catch block.

| Scope | Actions inside | Runs when |
|---|---|---|
| Try | All data retrieval, AI, composition, and distribution steps | Always |
| Catch | Error logging to SharePoint + failure alert email | Try scope fails or times out |

On failure: the distribution list receives a high-importance email with the error message and flow run ID, allowing immediate manual intervention.

Full error handling and governance documentation: [governance.md](governance.md)

---

## Key Design Decisions

**Azure Function as the AI proxy — not a direct HTTP call to Anthropic.** The Claude API key is stored as an encrypted Azure Function App Setting and never exposed to Power Automate. The flow only holds the function URL and a function-level key. This means the Anthropic key can be rotated without touching the flow, and it never appears in Power Platform's admin console.

**Audit record created before distribution begins.** The SharePoint audit write happens before the email send. If Outlook fails, a record with `RunStatus = "In Progress"` already exists. The Catch scope then creates a `[FAILED]` record. This ensures every run is traceable regardless of outcome — no silent failures.

**AI receives only items with issues — not the full list.** The payload to the Azure Function contains only the filtered items (non-compliant, open findings, missing fields), capped at 30 items. This keeps token counts predictable and focuses the AI summary on what actually needs attention. Passing all 500 items would produce unfocused summaries and unpredictable costs.

**All environment-specific values are flow parameters.** SharePoint URL, function URL, function key, Teams IDs, and distribution list are flow parameters — not hardcoded in action inputs. The same flow definition can be used in development and production by changing parameter values only.

---

## Trade-offs

| Decision | What was gained | What was given up |
|---|---|---|
| Power Automate over a scheduled Python script | Native M365 connectors; no server to manage; built-in run history | Less flexibility in error recovery; Premium licence required for HTTP action |
| Azure Function over Power Automate AI Builder | Full control over prompts; any Claude model; cost predictability | Additional Azure resource to deploy and maintain |
| SharePoint over Dataverse | No additional licence; existing compliance site | Limited relational capabilities; OData filter requires indexed columns |
| Try/Catch scope over per-action error handling | Clean separation of happy path and error path | A failure early in the Try scope skips all remaining steps, even if some could be retried safely |
| Inline HTML composition via concat() | No external template dependency; fully self-contained flow | Verbose flow expressions; harder to update the HTML layout without editing action inputs |

---

## What Was Learned

**Power Automate's parameterisation system is underused in practice.** Most flow examples online hardcode site URLs, keys, and IDs directly in action inputs. Using flow parameters from the start makes environment promotion (dev → UAT → prod) a configuration change rather than a re-build, and significantly reduces the risk of accidentally deploying a dev endpoint to production.

**The audit trail design changed the governance conversation.** Writing the audit record before distribution — rather than after — was a small decision that had a large practical consequence: every run is now traceable even if the flow crashes mid-execution. When the question "did the compliance report go out on 18 November?" comes up in an audit, the answer is in SharePoint, not in someone's memory.

**AI output schema must be validated in the flow, not assumed.** The first version of the Parse JSON action had a loose schema. When Claude returned a `trend_note` key with `null` instead of a string (for the first run with insufficient trend data), the flow threw a type mismatch error. The prompt was updated to specify the fallback text, and the Parse JSON schema was tightened to match the exact contract. This reinforced that the AI output contract needs the same rigour as any API contract.
