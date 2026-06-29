# Evaluation Scenario — Client Onboarding Automation for a 20-Person Remote Firm

## Organisation Profile

| Attribute | Detail |
|---|---|
| Type | B2B professional services (management consulting) |
| Size | 20 staff — 4 account managers, 10 consultants, 4 operations, 2 leadership |
| Revenue model | Retainer + project-based; 5–15 new clients per month |
| Tech stack | Google Workspace (Gmail, Drive, Calendar), HubSpot CRM, Asana, Slack, Stripe |
| M365 usage | None — not an Microsoft shop |
| Technical capability | Operations team can follow documented steps; no developer on staff |
| Budget sensitivity | High — every tool must justify its cost at this scale |

---

## The Problem Being Automated

When a new client is confirmed, the operations team manually completes the following steps — typically across a 2–3 hour window, often deferred until the next business day:

| Step | Manual action | Time cost |
|---|---|---|
| 1 | Copy client details from the signed proposal into HubSpot | 12 min |
| 2 | Send personalised welcome email (written from scratch each time) | 25 min |
| 3 | Create a project workspace in Asana from a template | 10 min |
| 4 | Post a "new client" message to the #clients Slack channel | 3 min |
| 5 | Create a contact in Mailchimp for the client newsletter | 5 min |
| 6 | Schedule a kickoff call invite via Google Calendar | 8 min |
| 7 | File the signed proposal in the correct Google Drive folder | 5 min |
| **Total** | | **~68 min per new client** |

At 10 new clients per month, this is approximately **11 hours of operational overhead per month** on a single repeatable workflow.

---

## Automation Requirements

### Functional requirements

1. **Trigger:** New row added to a Google Sheet (or form submission) when a client is confirmed
2. **CRM:** Create or update a HubSpot contact and deal record
3. **Email:** Generate and send a personalised welcome email (AI-generated, client-specific)
4. **Project management:** Create an Asana project from a template with client name and key dates
5. **Notifications:** Post a structured message to a Slack channel with client details
6. **Mailing list:** Add contact to Mailchimp audience
7. **Logging:** Write a record with timestamps to a Google Sheet audit log

### Non-functional requirements

| Requirement | Detail |
|---|---|
| Maintainability | A non-developer team member must be able to understand and modify the automation |
| Reliability | A failed step must alert someone rather than silently doing nothing |
| Cost | Total platform cost (including any AI usage) should not exceed ~$100/month at this scale |
| AI integration | Personalised email generation requires calling an AI API (OpenAI or Claude) |
| No-code preferred | The team does not want to manage a server or write code to operate the automation |

---

## Why This Scenario Tests the Platforms

This use case is deliberately representative of SME automation needs rather than an edge case:
- It spans 6 different apps (Google, HubSpot, Asana, Slack, Mailchimp, AI API)
- It requires AI-generated content (tests each platform's AI integration model)
- It requires error notification (tests reliability approach)
- It has a strict budget constraint (tests cost model at realistic SME volume)
- It must be maintainable by a non-developer (tests usability and long-term ownership)

A platform that handles this scenario well is genuinely useful to the business. A platform that handles it badly reveals limitations that will matter on day 31, not day 1.
