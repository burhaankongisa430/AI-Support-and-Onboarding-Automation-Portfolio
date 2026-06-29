# Platform Profiles

Detailed capability assessment for each platform against the defined scenario.
Scores justified with specific evidence — not opinion.

---

## Zapier

### Overview

Zapier is the most widely used no-code automation platform, with over 6,000 app connectors and a builder designed explicitly for non-technical users. It pioneered the "Zap" model: a linear trigger → action chain that is easy to read and explain to non-developers.

### Assessment by Criterion

**Cost at SME Scale — Score: 5/10**

The scenario requires ~150 runs/month (10 clients × 15 steps). Zapier counts each step as one "task":
- Free plan: 100 tasks/month (insufficient)
- Starter ($29.99/mo): 750 tasks — adequate for current volume but no room for growth
- Professional ($73.50/mo): 2,000 tasks — comfortable at current volume, needed if multi-step Zaps exceed 5 steps

For the full onboarding pipeline (7 steps + error branching ≈ 9 steps per client × 10 clients = ~90 tasks/month for the core flow), the Starter plan is technically sufficient today. But Zapier's task model means any increase in clients or steps quickly pushes you to the Professional tier.

The problem: at 25 clients/month, the Starter plan runs out. The Professional plan at $73.50/mo is acceptable, but Zapier charges by step rather than by run, creating unpredictable costs as workflows grow.

**Effective monthly cost for this scenario:** $29.99–$73.50 depending on growth trajectory.

---

**Ease of Implementation — Score: 9/10**

Zapier is the clearest choice for a non-technical user building their first automation:
- Linear trigger → action model is immediately intuitive
- Test buttons at each step show exactly what data flows through
- Error messages are plain English ("The email field is required")
- Extensive documentation and community forum for every connector
- Non-developer can build the full scenario in 2–4 hours with no prior experience

The primary usability weakness: Zapier's multi-step Zaps (needed for branching logic — e.g. "if HubSpot returns an error, send a Slack alert") require the Professional plan and are more complex to design. The linear model breaks down when the workflow needs conditional logic.

For **maintenance**: a colleague who did not build the Zap can read it top-to-bottom and understand what it does. This is a meaningful operational advantage.

---

**AI Integration Depth — Score: 6/10**

Zapier has a native "AI by Zapier" action and a ChatGPT connector. However:
- The ChatGPT connector works but is restricted to the OpenAI API — Claude (Anthropic) requires using the "Webhooks by Zapier" action (Premium) as an HTTP call
- Passing dynamic context (client name, industry, use case) into a prompt requires careful field mapping — no prompt template UI, so the prompt is constructed by concatenating Zap fields inline
- Parsing a JSON response from Claude (extracting the `subject` and `body` fields) requires either a "Code by Zapier" step (requires JavaScript) or a "Formatter by Zapier" step — neither is seamless for a non-developer
- There is no retry logic if the AI call fails

In practice, a non-developer on Zapier can get a ChatGPT-generated welcome email working. Getting Claude specifically to work, with clean JSON output parsing, requires workarounds that push the tool beyond its no-code promise.

---

**Reliability & Error Handling — Score: 7/10**

- Zapier sends an email when a Zap fails — this is on by default
- Run history is available for each Zap with step-level output visible
- Zapier automatically retries failed tasks (up to 3 times by default)
- Error handling branches (Paths with "Error" condition) are available but only on Professional+
- No per-step retry configuration — it's all or nothing

For the scenario: if the HubSpot connector fails, Zapier will retry and email the admin. This is sufficient for an SME that can accept a 15-minute delay in onboarding completion. It is not sufficient for workflows where real-time execution is critical.

---

**Scalability — Score: 6/10**

Zapier scales in volume (by paying more per tier) but not well in complexity:
- Conditional branching (Paths) is available but limited to simple if/else
- No native looping (iterating over arrays requires workarounds)
- Multi-step AI pipelines (e.g. generate email → validate → revise) are awkward to build
- At 50+ clients/month the cost approaches $200/month (Professional 5k tasks)

Zapier is designed for simple, linear workflows. The onboarding scenario is at the upper end of what Zapier does well. Adding a second automation (e.g. monthly client health check) is straightforward. Building a complex branching pipeline with error recovery and AI feedback loops is not.

---

**Ecosystem & Connectors — Score: 10/10**

- Google Workspace (Gmail, Sheets, Calendar, Drive): native, maintained, excellent
- HubSpot: native connector with full CRM access (contacts, deals, companies)
- Asana: native connector (create project from template available)
- Slack: native, excellent
- Mailchimp: native
- Stripe: native

All 6 scenario apps are available as first-class native connectors. This is Zapier's defining strength — the breadth of connectors is unmatched.

---

**Governance & Auditability — Score: 5/10**

- Zap run history retained for 90 days on Professional; 7 days on Starter
- Step-level output visible in run history
- No version history for the Zap configuration itself — rolling back a change requires manual recreation
- Access control: Zapier Teams (paid add-on) allows multiple users; owner model on free/standard

For a 20-person firm, the 7-day run history on the Starter plan is inadequate for any meaningful audit. The Professional plan's 90 days is acceptable.

---

### Zapier Summary

| Strength | Weakness |
|---|---|
| Fastest to build; easiest for non-developers | Task-based pricing gets expensive as workflow grows |
| 6,000+ connectors; all scenario apps native | AI integration for Claude requires HTTP workaround + JS for parsing |
| Automatic retry; email alerts on failure | Limited branching logic; no loops |
| Excellent documentation | No version history for Zap configuration |

**Best suited for:** Teams that want automation running today with minimal investment in learning, and whose workflows are primarily linear trigger-to-action chains.

---

---

## Make (formerly Integromat)

### Overview

Make is a visual automation platform built around a canvas-based "scenario" model rather than Zapier's linear list. Modules (nodes on the canvas) are connected with routes, filters, and iterators. It is significantly more capable than Zapier for complex logic, and substantially cheaper at equivalent operation volumes.

### Assessment by Criterion

**Cost at SME Scale — Score: 9/10**

Make charges by **operations** — each module execution counts as one operation:
- Free plan: 1,000 ops/month (insufficient)
- Core ($9/mo): 10,000 ops/month
- Pro ($16/mo): 10,000 ops/month + advanced features (custom variables, full execution history)

For the scenario: ~9 modules × 10 clients = 90 operations/month. The Core plan at $9/month covers this with 111× headroom. Even at 100 new clients/month (900 operations), the Core plan is sufficient.

Make's pricing model is fundamentally more SME-friendly than Zapier's: it charges per module execution rather than per step, which is the same thing but at a far lower per-unit cost. The operation count only becomes a concern at enterprise automation volumes.

**Effective monthly cost for this scenario:** $9–$16/month.

---

**Ease of Implementation — Score: 7/10**

The canvas UI is more powerful than Zapier's linear list, but the learning curve is steeper:
- Connecting modules visually is intuitive once you understand the model
- The first hour is disorienting — the canvas metaphor is unfamiliar to non-technical users
- Data mapping uses a panel with nested field pickers — more powerful than Zapier's inline fields but more confusing initially
- Filters (conditions between modules) are configured in a separate panel, not inline
- Error handlers are modules on the canvas — visual and explicit once you know they exist

For a non-developer, building the full scenario in Make takes approximately 6–10 hours the first time, versus 2–4 hours in Zapier. However, Make scenarios are easier to read visually once built — the canvas layout shows the full flow at a glance.

**Maintenance:** A colleague who understands the basic module model can navigate an existing scenario without difficulty. The canvas is more self-documenting than Zapier's step list for complex flows.

---

**AI Integration Depth — Score: 8/10**

Make has a native OpenAI module (supports GPT-4, GPT-4o, DALL·E). For Claude specifically:
- Use the HTTP module with a POST request to `api.anthropic.com/v1/messages`
- Set headers (API key, version, content-type) in the HTTP module config
- Body uses Make's JSON template syntax — dynamic fields (client name, use case) are inserted cleanly using the data picker
- Response is parsed automatically by Make's JSON parser — access `body.content[0].text` directly in subsequent modules

In practice, the HTTP → Claude → Parse JSON chain in Make is cleaner than Zapier's equivalent because:
1. Make's HTTP module has full JSON body configuration with a visual builder
2. The JSON response is parsed by Make into navigable fields without a separate parsing step
3. No JavaScript required at any point

The only limitation: the HTTP module requires specifying headers manually (Content-Type, x-api-key, anthropic-version) — a 10-minute setup task documented clearly in the Claude API docs.

---

**Reliability & Error Handling — Score: 8/10**

Make's error handling is module-level, not flow-level:
- Each module can have an error handler route (a separate path on the canvas that triggers on failure)
- Error handlers can be set to: Resume, Rollback, Commit, Ignore, or Break (halt scenario)
- Built-in retry: configurable per module (up to 5 retries with delay)
- Email notifications when a scenario fails: configurable
- Execution history: available for every run with input/output at each module; retained for 30 days on Core

For the scenario: if the HubSpot module fails, the error handler route can send a Slack message, then Break (halt the scenario). This is more granular than Zapier — you control the failure behaviour per step.

The visual error handler on the canvas is also more legible than Zapier's hidden error branch logic — a maintainer can see the error path directly.

---

**Scalability — Score: 8/10**

Make's scenario model handles complexity that Zapier cannot:
- Iterators: loop over arrays (e.g. multiple contacts in a single Asana project)
- Aggregators: collect module outputs and process them as a batch
- Routers: multi-branch conditional logic with filters
- Sub-scenarios: call one scenario from another (available on Pro+)

At higher volumes, Make's operation-based pricing scales gracefully — 50,000 ops/month on the Pro plan at $16/month would cover 5,000+ onboarding runs. Pricing tiers above Pro (Teams, Enterprise) are available if needed.

Make is also actively developed, with AI/LLM features being added regularly. It is a platform that will grow alongside AI automation demands.

---

**Ecosystem & Connectors — Score: 8/10**

- Google Workspace (Gmail, Sheets, Calendar, Drive): native, well-maintained
- HubSpot: native connector (contacts, deals, CRM activities)
- Asana: native connector (create projects, tasks, sections)
- Slack: native, excellent
- Mailchimp: native
- Stripe: native

All 6 scenario apps are available as native connectors. The depth of the Asana connector is slightly less than Zapier's (fewer pre-built actions), but sufficient for the scenario. Make has approximately 1,500+ connectors — less than Zapier's 6,000 but covering all mainstream business apps.

---

**Governance & Auditability — Score: 6/10**

- Execution history retained for 30 days (Core); unlimited on higher tiers
- Each execution shows module-level input/output
- Scenario version history is not available — but scenarios can be cloned manually as backups
- Access control: Organisation feature allows team members with different roles
- No native audit log export (would require building a logging step into each scenario)

For the scenario: the 30-day execution history is sufficient. The lack of version history is the main governance gap — a Make scenario changed by a team member cannot be rolled back to a previous version.

---

### Make Summary

| Strength | Weakness |
|---|---|
| Lowest cost at SME scale ($9/mo) | Steeper initial learning curve than Zapier |
| Visual canvas shows full flow complexity | No version history for scenario config |
| Best AI integration via HTTP (no code, clean JSON) | Fewer connectors than Zapier (1,500 vs 6,000) |
| Per-module error handling with configurable retry | Canvas UI unfamiliar to first-time users |
| Scales to complex logic (loops, branches, sub-scenarios) | |

**Best suited for:** Teams that can invest a day of initial setup time in exchange for significantly lower ongoing cost and meaningfully better support for AI and complex logic.

---

---

## Power Automate

### Overview

Power Automate (formerly Microsoft Flow) is Microsoft's enterprise automation platform, deeply integrated with the Microsoft 365 ecosystem. It offers cloud flows, desktop flows (RPA), and AI Builder capabilities. It is the standard choice for organisations running Microsoft 365 as their primary toolset.

### Assessment by Criterion

**Cost at SME Scale — Score: 6/10**

Power Automate pricing is tied to Microsoft licences:
- **Included with M365 Business Premium ($22/user/mo):** Standard connectors only (no HTTP action, no premium app connectors)
- **Power Automate Premium ($15/user/mo):** Required for HTTP action, HubSpot connector, and most third-party connectors outside the M365 ecosystem
- **Power Automate Process ($150/process/mo):** Unattended automation at higher volumes

For this scenario, the HTTP action (needed for Claude API) and the HubSpot connector are both **premium connectors**. This means the $15/user/month Power Automate Premium licence is required — minimum.

For a 20-person firm where 2 people manage automations: **$30/month** for the Power Automate Premium licences.

**However:** This firm does not use M365. The Google Workspace connector in Power Automate is available but requires a premium licence, and the native Google Sheets integration is less capable than Zapier's or Make's. Building this scenario in Power Automate on a non-M365 stack would require HTTP calls to multiple Google APIs — significantly increasing build complexity.

**Effective monthly cost for this scenario (non-M365 firm):** $30–60/month for licences, plus additional development time to work around native connector limitations.

---

**Ease of Implementation — Score: 4/10**

Power Automate's flow builder is more capable than Zapier but significantly harder to use for a non-developer:
- The UI uses Microsoft's design language — familiar to M365 users but unfamiliar to Google Workspace users
- Actions are found through a search panel rather than a visual canvas
- Dynamic content (field mapping) requires understanding the "dynamic content" picker, which can be confusing when dealing with arrays or nested JSON
- Error handling (Try/Catch scope) requires understanding the scope concept and `runAfter` configuration — not intuitive without prior exposure
- The HTTP action (needed for Claude) requires manually specifying method, headers, and JSON body — more configuration than Make's HTTP module

A non-developer at a non-M365 firm would find Power Automate materially harder to build and maintain than either Zapier or Make. The concepts are enterprise-oriented and assume some familiarity with the Microsoft ecosystem.

**Maintenance:** Non-developer maintenance is possible for simple flows but challenging for anything involving HTTP actions, JSON parsing, or error scopes. The likelihood of needing developer support for modifications is higher than with either alternative.

---

**AI Integration Depth — Score: 7/10**

Power Automate has two paths for AI integration:
1. **AI Builder:** Microsoft's native AI service — includes pre-built models (sentiment analysis, form processing, image recognition) and a prompt-based text generation model powered by GPT. Available on the AI Builder add-on (~$500/month for full capacity, or pay-per-credit).
2. **HTTP action:** POST to any API including Claude — requires manual header configuration, body composition, and JSON response parsing via Parse JSON action.

For the scenario:
- AI Builder's text generation model can write the welcome email without the HTTP action — but the model is GPT-based (not Claude), the prompt is configured in a simplified UI, and the output quality and flexibility are lower than calling Claude directly.
- The HTTP → Claude path works (see Project 4 in this portfolio for a working example) but requires premium licence, careful JSON setup, and a Parse JSON action.

Score reflects that Power Automate can do AI integration, but it costs more (AI Builder add-on) or requires more configuration (HTTP path) than Make's equivalent.

---

**Reliability & Error Handling — Score: 9/10**

Power Automate's error handling is the strongest of the three platforms:
- Scope Try/Catch pattern provides structured error boundaries (see [Project 4](../../Project-04-Power-Automate-M365))
- `runAfter` conditions allow fine-grained control over which actions run on success, failure, timeout, or skip
- Concurrency control: prevent duplicate runs if a trigger fires simultaneously
- Built-in retry policy: configurable per action (fixed interval or exponential backoff, up to 90 minutes)
- Run history: 28 days, step-level detail, available in the Power Automate portal

For the scenario, this is the most reliable platform. An enterprise pattern (Try/Catch + audit log) can be implemented directly in the flow. However, this reliability comes at the cost of build complexity — the error scope pattern is not intuitive for a non-developer.

---

**Scalability — Score: 9/10**

Power Automate is enterprise-grade automation software. It scales to:
- Complex branching logic (Switch, Conditions, nested scopes)
- Apply to Each (loops over arrays)
- Parallel branches
- Child flows (sub-processes called from a parent flow)
- Desktop flows for RPA (automating non-API applications)
- Dataverse integration for structured enterprise data at scale

At the scale of this scenario (150 runs/month), Power Automate is massively over-specified. Its scalability is relevant if the firm grows to enterprise scale, but that is a hypothetical future state that should not drive today's decision.

---

**Ecosystem & Connectors — Score: 7/10**

- Google Workspace: available but limited to standard/premium depending on connector; less seamless than native Zapier/Make integration
- HubSpot: premium connector — requires Premium licence
- Asana: premium connector — requires Premium licence
- Slack: available
- Mailchimp: available (standard)
- Stripe: available (standard)

For a **Microsoft 365 shop**, Power Automate's connector depth for M365 apps (SharePoint, Teams, Outlook, Planner, Dataverse) is unmatched. For a **Google Workspace shop**, the native connector advantage disappears — most required connectors become premium, and Google API integration requires HTTP workarounds.

This firm runs Google Workspace. The connector advantage of Power Automate does not apply here.

---

**Governance & Auditability — Score: 9/10**

- 28-day run history with step-level input/output detail
- Flow version history available in the flow detail view
- Environment-based access control (Dev / UAT / Production environments available)
- Data loss prevention (DLP) policies configurable at the tenant level
- Audit log integration with Microsoft Purview for enterprise compliance
- Connection ownership and sharing configurable at the connection level

Power Automate's governance model is enterprise-grade and the best of the three platforms by a significant margin. For regulated industries or organisations with strict data governance requirements, this matters. For a 20-person professional services firm on Google Workspace, most of this governance infrastructure is unused overhead.

---

### Power Automate Summary

| Strength | Weakness |
|---|---|
| Best-in-class error handling and retry | Designed for M365 — poor fit for Google Workspace shops |
| Enterprise governance, DLP, version history | Highest learning curve; not maintainable by non-developers |
| Deepest M365 integration (Teams, SharePoint, Planner) | Premium licence required for HTTP action and key connectors |
| Scales to enterprise complexity | Overkill at 20-person scale; complexity without proportional benefit |
| AI Builder for no-code AI (at extra cost) | AI Builder adds significant cost; HTTP path requires developer-level config |

**Best suited for:** Organisations already running Microsoft 365 as their primary platform, with IT governance requirements, and access to a developer or Power Platform specialist.
