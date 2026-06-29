# SharePoint List Schema

## List 1 — Compliance Checks

**Purpose:** Source data. Compliance owners update this list weekly with the status of each check they own.
**Location:** `https://yourorg.sharepoint.com/sites/Compliance/Lists/Compliance Checks`

| Column | Type | Required | Options / Notes |
|---|---|---|---|
| Title (CheckName) | Single line text | Yes | Name of the specific compliance check |
| ComplianceArea | Choice | Yes | Data Privacy · Financial Controls · IT Security · HR Compliance · Operational |
| Status | Choice | Yes | Compliant · Non-Compliant · In Remediation · Under Review · Archived |
| Owner | Person | Yes | Responsible team member |
| DueDate | Date | Yes | Expected resolution date (for non-compliant items) |
| FindingCount | Number | No | Number of open findings; 0 = no findings |
| RiskLevel | Choice | Yes | Low · Medium · High · Critical |
| Notes | Multi-line text | No | Additional context from the owner |
| Modified | Date/time | Auto | Updated by SharePoint automatically |
| Created | Date/time | Auto | Set by SharePoint automatically |

**Indexing:** Index the `Modified` column to ensure OData filter queries (`Modified ge '{date}'`) perform well at scale.

**Permissions:**
- Compliance owners: Edit (their own items)
- Compliance managers: Edit all
- Report consumers: Read
- Power Automate service account: Read

---

## List 2 — Report Audit Log

**Purpose:** Immutable run history. Written by Power Automate on every execution (success or failure). Used for governance, SLA tracking, and incident investigation.
**Location:** `https://yourorg.sharepoint.com/sites/Compliance/Lists/Report Audit Log`

| Column | Type | Notes |
|---|---|---|
| Title | Single line text | Report name e.g. "Weekly Compliance Report — w/c 18 Nov 2024"; prefix "[FAILED]" on error |
| RunTimestamp | Date/time | UTC timestamp when the flow run started |
| TotalChecks | Number | Count of compliance items reviewed this period |
| ItemsWithIssues | Number | Count of non-compliant / flagged items |
| AISummaryGenerated | Yes/No | True if the Azure Function returned successfully |
| EmailSent | Yes/No | True if Outlook delivery succeeded |
| TeamsPostSent | Yes/No | True if Teams post succeeded |
| RunStatus | Choice | In Progress · Completed · Failed |
| ErrorDetails | Multi-line text | JSON error blob written on failure; empty on success |

**Permissions:**
- Power Automate service account: Edit (to create and update records)
- Compliance managers: Read
- All others: No access (audit log is internal to the automation)

**Retention:** Do not delete items. Items should be retained for a minimum of 3 years for audit purposes. Configure a SharePoint retention policy accordingly.

---

## Governance Notes

**Why two separate lists?** The Compliance Checks list is owned by the business — compliance officers update it. The Report Audit Log is owned by the automation — only Power Automate writes to it. Mixing them would create permission conflicts and make the audit record mutable by end users.

**Why SharePoint over Dataverse?** SharePoint was chosen because:
1. The organisation already had a SharePoint compliance site with existing data
2. No premium Dataverse licence was required
3. The OData filter capabilities of the SharePoint connector meet the query requirements

If the data model grows (relationships, calculated columns, complex queries), migrating to Dataverse would be the appropriate next step.
