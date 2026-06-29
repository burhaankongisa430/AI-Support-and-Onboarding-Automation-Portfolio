# Final Recommendation

## Primary Recommendation: Make

**For a 20-person remote professional services firm on Google Workspace, with no in-house developer
and a ~$100/month automation budget: build the client onboarding pipeline on Make.**

---

## Business Justification

### 1. Cost argument is decisive at this scale

Make's Core plan at **$9/month** covers the full scenario with 111× operational headroom. Zapier's
Professional plan at **$73.50/month** is the realistic starting point for the same workflow with
comparable room to grow. That is a **$780/year difference** for functionally equivalent automation —
a material line item for a 20-person firm.

At 5× current volume (50 new clients/month), both platforms stay within their current plans. At 20×
volume (200 clients/month), Zapier moves to a higher tier (~$200/month) while Make requires only a
$16/month Pro plan upgrade. The cost gap compounds with growth.

### 2. AI integration quality matters more than speed of first build

The highest-weighted criterion (25%) is AI integration depth — and Make is the better platform for it.

The specific need (Claude API → personalised welcome email with dynamic client context → JSON parsing
back into the workflow) is handled in Make via: HTTP module → JSON response automatically parsed → fields
available in subsequent modules. No code. No JavaScript. No workarounds.

In Zapier, the equivalent requires: Webhooks by Zapier (premium) → Code by Zapier with JavaScript to
parse the response → field mapping. A non-developer cannot build or maintain the Zapier version of this
step independently.

The AI-generated welcome email is the highest-value step in the entire pipeline. Getting that step right
— and keeping it maintainable — is worth accepting a 4–6 hour longer initial build time.

### 3. The firm will grow into Make's capabilities

Make supports loops, multi-branch routing, sub-scenarios, and aggregators. These are not needed on day 1
but will be needed as the automation library grows. Building on Make now avoids a platform migration in
18 months when the linear Zapier model hits its limits.

Zapier's architecture is fundamentally a list of trigger → actions. The moment the firm wants to loop
over multiple contacts, branch based on client industry, or call one automation from another, Zapier
requires workarounds or a rebuild. Make supports this natively.

---

## Conditions Under Which to Reconsider

### Choose Zapier instead if:
- The automation is needed in the next 72 hours with no time for learning a new tool
- The person maintaining it long-term has zero prior automation experience and cannot invest in a learning day
- The firm's tool stack expands significantly and connector breadth becomes the primary concern
- Budget is truly not a factor ($73.50/month vs $9/month is irrelevant)

### Choose Power Automate instead if:
- The firm adopts Microsoft 365 as its primary productivity suite (Teams, SharePoint, Outlook)
- There are compliance or data governance requirements that need DLP policies, environment separation, or enterprise audit trails
- A Power Platform specialist or developer is available to build and maintain the flows
- The firm is in a regulated industry where Power Automate's enterprise-grade governance is a requirement, not a preference

---

## Implementation Path on Make

| Phase | Actions | Timeline |
|---|---|---|
| **Day 1** | Create Make account (Core plan, $9/mo); connect Google Sheets, HubSpot, Asana, Slack, Mailchimp connectors | 2–3 hours |
| **Day 1–2** | Build the trigger → HubSpot → Asana → Slack → Mailchimp linear path; test with a real client | 4–6 hours |
| **Day 2** | Add the HTTP → Claude AI email step; configure prompt with client context fields; test output | 3–4 hours |
| **Day 2** | Add error handler routes (at minimum: HTTP failure → Slack alert) | 1 hour |
| **Day 3** | Add Google Sheet audit log step; end-to-end test with 3 mock clients | 2 hours |
| **Week 2** | Run live for real clients; monitor execution history for errors; refine AI prompt | Ongoing |

**Total build time estimate:** 12–16 hours across 3 days for a non-developer following documentation.

---

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Make's AI HTTP integration requires more initial setup than expected | Medium | Follow the Claude API docs exactly; the HTTP module config is a 10-minute task once you have the API key |
| Non-developer gets stuck during initial build | Medium | Make has a strong community forum and video tutorials; budget one day of external consultant time as a contingency |
| Make changes its pricing model | Low | Monitor pricing annually; at $9/month the budget has significant headroom before a price increase matters |
| The firm moves to Microsoft 365 | Low–Medium | If M365 adoption happens, evaluate Power Automate at that point; Make and PA automations are not directly portable but the logic is transferable |
| A scenario breaks silently | Low | Configure email failure alerts on every scenario (Make → Notifications settings); review execution history weekly in the first month |

---

## Conclusion

Make is the right platform for this firm today. It is the lowest-cost option, the best AI integration path, and the most capable platform for the complexity the firm will grow into — all without requiring a developer to build or maintain it.

Zapier would be a reasonable second choice for teams optimising for speed of first deployment.
Power Automate would be the right answer if, and only if, the firm's operational context changes — specifically, if it adopts Microsoft 365 as its primary toolset.

The recommendation is to proceed with Make, invest one training day in the initial build, and treat the $780/year in saved platform costs as the first tangible return on the automation investment.
