# Flow Description — Weekly Compliance Report

**Trigger:** Recurrence — every Monday at 07:00 EST
**Environment:** Power Automate Cloud (Premium)
**Connections required:** SharePoint, Office 365 Outlook, Microsoft Teams, HTTP

---

## Flow Map

```
[TRIGGER] Recurrence — Monday 07:00 EST
    │
    ├─ Initialize: ReportStartDate (utcNow() - 7 days)
    ├─ Initialize: ReportTitle ("Weekly Compliance Report — w/c {date}")
    ├─ Initialize: HasErrors (false)
    │
    └─ SCOPE: Try
        │
        ├─ [SP] Get Items — "Compliance Checks" list
        │       Filter: Modified >= ReportStartDate
        │       Order: ComplianceArea asc, Modified desc
        │       Top: 500
        │
        ├─ [Filter] Exclude Archived items
        │
        ├─ [Select] Validate_RequiredFields
        │           → Map each item; compute MissingFields string
        │
        ├─ [Filter] Items with issues
        │           → Status != Compliant  OR  FindingCount > 0  OR  MissingFields not empty
        │
        ├─ [Compose] SummaryPayload
        │            → { report_title, report_period, total_checks,
        │                items_with_issues, compliant_count, items[] }
        │
        ├─ [HTTP POST] Azure Function — /api/generate-summary
        │              → Body: SummaryPayload
        │              → Response: { executive_summary, key_findings,
        │                            risk_assessment, recommended_actions, trend_note }
        │
        ├─ [Parse JSON] AISummaryResponse
        │
        ├─ [Compose] HTMLReport
        │            → Full HTML email: stats table + AI sections
        │
        ├─ [SP] Create item — "Report Audit Log"
        │       Status = "In Progress", EmailSent = false, TeamsPostSent = false
        │
        ├─ [Outlook] Send Email
        │            → To: distribution list  Subject: ReportTitle  Body: HTMLReport
        │
        ├─ [SP] Patch Audit Record → EmailSent = true
        │
        ├─ [Teams] Post to Compliance channel
        │          → Card: title + executive_summary + stats
        │
        └─ [SP] Patch Audit Record → TeamsPostSent = true, RunStatus = "Completed"

    └─ SCOPE: Catch  (runs on: Failed, TimedOut)
        │
        ├─ Set HasErrors = true
        ├─ Compose ErrorDetails
        ├─ [SP] Create error record in Audit Log (RunStatus = "Failed")
        └─ [Outlook] Send failure alert email (Importance: High)
```

---

## Action-by-Action Detail

### Variables

| Variable | Type | Value | Purpose |
|---|---|---|---|
| `ReportStartDate` | String | `utcNow() - 7 days` (ISO 8601) | SharePoint filter boundary |
| `ReportTitle` | String | `"Weekly Compliance Report — w/c {date}"` | Consistent identifier across email, Teams, audit log |
| `HasErrors` | Boolean | `false` (default) | Set to `true` in Catch scope; available to downstream monitoring |

### Get_ComplianceItems

- **Connector:** SharePoint — Get Items
- **Filter:** `Modified ge '@{variables('ReportStartDate')}'` (OData)
- **Top:** 500 items — prevents pagination complexity while covering realistic weekly volumes
- **Order:** `ComplianceArea asc, Modified desc` — groups related items for the AI summariser

### Filter_ExcludeArchived

- Array filter: `Status != "Archived"`
- Archived items are historical records that have been reviewed and closed; including them would distort the current-period counts

### Validate_RequiredFields (Select action)

Maps each item and adds a `MissingFields` computed string:
```
MissingFields = concat(
    if(empty(Owner), 'Owner;', ''),
    if(empty(DueDate), 'DueDate;', ''),
    if(empty(RiskLevel), 'RiskLevel;', '')
)
```
Items with a non-empty `MissingFields` are treated as data quality issues and included in the "require attention" count even if their Status is Compliant.

### HTTP_GenerateAISummary

- **Method:** POST
- **URL:** Azure Function endpoint (parameterised — never hardcoded)
- **Auth:** `x-functions-key` header (Function-level auth key, stored in flow parameter `AISummaryFunctionKey`)
- **Body:** `SummaryPayload` (report metadata + only the items that have issues — not the full list, to stay within token limits)
- **Timeout:** Power Automate default HTTP timeout is 120 seconds; the Azure Function completes in under 10 s for typical volumes

### Compose_HTMLReport

Builds a complete HTML email inline using Power Automate `concat()` expressions. No external template dependency — the flow is self-contained.

Sections:
1. Header with report title and period
2. Summary stats table (total / compliant / require attention)
3. Executive Summary (AI)
4. Risk Assessment (AI)
5. Key Findings (AI — bulleted list)
6. Recommended Actions (AI — bulleted list)
7. Auto-generated footer with timestamp

### SharePoint Audit Log (two writes)

**Write 1 (before distribution):** Creates the audit record with `RunStatus = "In Progress"`. This means a record always exists even if the email or Teams step fails — the error scope can then update it.

**Write 2 (after Teams post):** Updates `TeamsPostSent = true` and `RunStatus = "Completed"`. Two separate writes allow partial completion tracking if the Teams step fails after the email succeeds.

### Error Scope

- Runs on: `Failed` or `TimedOut` of the Try scope
- Writes a `[FAILED]` record to the audit log with the error message and flow run ID
- Sends a high-importance failure alert email to the same distribution list
- Does **not** suppress the error — the flow run itself shows as failed in the Power Automate run history

---

## Key Design Choices

**Parameterised URLs and credentials** — all environment-specific values (SharePoint URL, function URL, function key, Teams channel IDs, distribution list) are defined as flow parameters rather than hardcoded in action inputs. This allows the flow to be promoted between development, UAT, and production environments by changing parameter values only.

**Audit log written before distribution** — if Outlook or Teams fails, the audit record already exists with `RunStatus = "In Progress"`. The error scope updates it to `Failed`. This ensures every run is traceable regardless of outcome.

**AI receives only issue items** — the `items` array in the AI payload contains only the filtered (non-compliant / missing fields) items, not the full compliance list. This keeps the token count predictable and focuses the AI summary on what actually needs attention.

**Try/Catch scope pattern** — Power Automate's scope action with `runAfter` conditions of `["Failed", "TimedOut"]` is the closest equivalent to a try/catch block. All critical actions are inside the Try scope so a single action failure triggers the full catch behaviour.
