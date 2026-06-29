# Error Handling & Governance

## Error Handling Strategy

### Try/Catch Pattern

Power Automate does not have native try/catch, but the `Scope` action with conditional `runAfter` achieves equivalent behaviour:

```
Scope "Try"
    ← all critical actions

Scope "Catch"
    runAfter: { "Scope_Try": ["Failed", "TimedOut"] }
    ← error logging and failure alert
```

**What triggers the Catch scope:**
- Any action inside the Try scope fails (HTTP error, SharePoint timeout, connection issue)
- The Try scope times out (Power Automate default: 30 days for cloud flows, but the HTTP timeout on the Azure Function call is 120 seconds)

**What the Catch scope does:**
1. Sets `HasErrors = true` (variable available to any future monitoring expressions)
2. Composes error details (flow run ID, error message, timestamp)
3. Creates a `[FAILED]` audit record in SharePoint
4. Sends a high-importance failure alert email to the same distribution list the report would have gone to

**What the Catch scope does NOT do:**
- It does not retry the failed operation — retries would risk duplicate email delivery
- It does not suppress the error — the Power Automate run history correctly shows the run as Failed

---

### Partial Failure Handling

Not all steps carry the same consequence if they fail:

| Action | Failure consequence | Mitigation |
|---|---|---|
| Get_ComplianceItems | No data to report | Catch scope fires; failure alert sent |
| HTTP_GenerateAISummary | No AI content | Catch scope fires; failure alert sent |
| Outlook_SendReport | Report not delivered | Catch scope fires; failure alert sent |
| Teams_PostSummaryCard | Channel not notified | Audit record still created; email still delivered; no separate alert (low severity) |
| SharePoint audit updates | Run not fully logged | Accepted risk — audit data may be incomplete but the report was delivered |

The Teams post and SharePoint audit updates are placed after the email send in the flow, so if they fail the report has already been delivered. The audit record created at step 9 already exists — the patch updates are additive improvements, not critical writes.

---

### Azure Function Error Handling

The Azure Function returns structured errors with appropriate HTTP status codes:

| Scenario | HTTP status | Response body |
|---|---|---|
| Invalid JSON body | 400 | `{"error": "Invalid JSON body"}` |
| Missing required fields | 400 | `{"error": "missing_fields", "fields": [...]}` |
| Claude API failure | 502 | `{"error": "AI generation failed", "detail": "..."}` |
| JSON parse error in Claude response | 502 | `{"error": "AI response parse error", "detail": "..."}` |
| Success | 200 | `{"executive_summary": ..., ...}` |

When Power Automate receives a 4xx or 5xx from the HTTP action, it marks the action as Failed, which triggers the Try scope to fail and the Catch scope to run.

---

## Governance Approach

### 1. Audit Trail

Every flow execution writes to the SharePoint **Report Audit Log** regardless of outcome. The log is:
- Written at start (In Progress) to capture runs that never complete
- Updated on success (Completed) and failure (Failed)
- Never deleted — retained for a minimum of 3 years per information governance policy
- Accessible to compliance managers for investigation but not modifiable by end users

This means every question of the form "did the report run on week X?" can be answered by querying the audit log list.

### 2. Credential Management

| Credential | Where stored | Who can see it | Rotation |
|---|---|---|---|
| SharePoint / Outlook / Teams OAuth | Power Automate connection | Connection owner; Power Platform admin | On service account password change |
| Azure Function key (`AISummaryFunctionKey`) | Power Automate flow parameter (SecureString) | Flow owner; Power Platform admin | Manually via Azure portal |
| Anthropic API key | Azure Function App Setting | Azure subscription admin only | Manually via Azure portal |

The Anthropic API key **never appears in the Power Automate flow**. The flow only knows the function URL and function key. This means:
- Rotating the Anthropic key requires no changes to the Power Automate flow
- The key is protected by Azure's encrypted App Settings store
- No Anthropic credentials are visible in Power Platform's admin console

### 3. Connection Accounts

The flow uses a **dedicated service account** (`compliance-automation@yourorg.com`) for all M365 connections. This account:
- Has the minimum permissions required (SharePoint Read + Edit on two lists; Outlook Send-as; Teams post)
- Is not a named user account — unavailability due to leave/departure does not affect the flow
- Is excluded from MFA conditional access policies that would break unattended automation
- Is licensed for Power Automate Premium

### 4. Flow Ownership and Change Control

- **Owner:** Compliance Operations team (not IT)
- **Co-owner:** IT Automation team (for technical maintenance)
- **Change process:** All changes to the flow must be tested in the Power Automate development environment before promotion to production. Changes affecting the AI prompt or output schema must be validated against the sample data in `sample_data/` to confirm the response parses correctly.
- **Version history:** Power Automate maintains a 28-day version history automatically. Significant changes should be documented in the CHANGELOG section of this file.

### 5. Monitoring

- **Run history:** Visible in Power Automate → My Flows → [Flow name] → Run History. Failures appear immediately.
- **Failure alert:** The Catch scope sends a high-importance email to the distribution list when the flow fails. This acts as the primary alert mechanism.
- **Audit log review:** Compliance managers review the SharePoint Audit Log as part of the monthly governance review to confirm all weekly runs completed.
- **Azure Function monitoring:** Application Insights is enabled on the function app. Query for `exceptions` and `requests` with result code != 200 to identify AI generation issues.

---

## CHANGELOG

| Date | Change | Author |
|---|---|---|
| Initial | Flow created and deployed | Burhaan Mziwakhe Kongisa |
