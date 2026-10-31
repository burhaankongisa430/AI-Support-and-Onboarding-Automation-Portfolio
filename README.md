# AI-Support-Automation-Portfolio

A portfolio of five projects structured as a deliberate progression; from embedding AI into a live operational workflow, through strategic process thinking, into multi-system orchestration, enterprise platform depth, and finally advisory-level tool evaluation. Moving through the projects from 1 to 5 is a clear arc: core AI integration skills, strategic architecture thinking, connected system design, enterprise Microsoft 365 depth, and the ability to advise leadership on platform investment decisions.

Each project is a layer in that progression, as apposed to five independent tutorials. The AI integration pattern established in Project 1 reappears in Projects 3 and 4 at greater complexity. The process architecture thinking in Project 2 informs the design decisions documented in Projects 3 and 4. The platforms compared in Project 5 are the same platforms used to build the earlier projects, so the evaluation is grounded in hands-on experience, not theory.

Each project folder contains its own detailed README covering the business problem, architecture, design decisions, trade-offs, and what was learned.

---

## Portfolio at a Glance

| # | Project | Layer | Key Tools |
|---|---------|-------|-----------|
| 1 | [AI-Assisted Operational Workflow](#project-1--ai-assisted-operational-workflow) | Foundation | Claude API, Flask, Airtable, Zapier |
| 2 | [Process Optimisation Case Study](#project-2--process-optimisation-case-study) | Strategy | Python, Mermaid, Architecture Decision Records |
| 3 | [Multi-Tool Automation Orchestration](#project-3--multi-tool-automation-orchestration) | Complexity | Claude API, SendGrid, Slack, Airtable, Flask |
| 4 | [Power Automate + Microsoft 365](#project-4--power-automate--microsoft-365) | Platform Depth | Power Automate, Azure Functions, SharePoint, Teams |
| 5 | [AI Tool Evaluation Report](#project-5--ai-tool-evaluation-report) | Advisory | Zapier, Make, Power Automate, scoring model |

---

## Project Summaries

### Project 1 — AI-Assisted Operational Workflow

**Folder:** `Project-01-AI-Operational-Workflow/`

A webhook server that receives incoming support tickets from any source (Google Form, Zapier, direct HTTP), sends them through Claude to classify urgency, extract key issues, and draft a professional response, then creates an enriched record in Airtable with the triage results. Every ticket is classified and ready for an agent before a human ever opens the queue.

**What it demonstrates:** Embedding AI as a functional layer inside a real operational process, not a chatbot. Claude is architected into a workflow as a structured classification and content-generation engine. Prompt design decisions (JSON-only output contract, enumerated field constraints, word-count bounds) are documented separately with rationale so the reader can see the engineering behind the prompt, not just the prompt itself.

**Key design decisions:** Claude Sonnet over Haiku for higher accuracy on nuanced sentiment; single synchronous API call per ticket for simplicity; Airtable as a zero-infrastructure CRM; enumerated urgency and category values in the prompt to keep classification deterministic and validatable in code.

---

### Project 2 — Process Optimisation Case Study

**Folder:** `Project-02-Process-Optimisation-Case-Study/`

A documented case study of a real workflow automation initiative contributed to at a large cloud services organisation: replacing a manual, inbox-based support case handling process with automated intake, classification, round-robin assignment, SLA tracking, and proactive escalation. Includes before/after Mermaid process maps, a full metric comparison (−98% mean time to assignment, −91% SLA breach rate), three Architecture Decision Records, and a Python simulator that runs the core automation logic with sample data.

**What it demonstrates:** Architect-level strategic thinking. Identifying a real operational problem, mapping the current state, designing the future state, and quantifying the improvement with honest metrics and confidence notes. The ADRs show the reasoning behind choosing a rules engine over an ML classifier, polling over event timers, and a structured intake form over free-form email. All system names and team identifiers have been generalised to protect confidential information.

**How it builds on Project 1:** Where Project 1 uses AI to solve the classification problem, Project 2 demonstrates that the right tool for classification is sometimes a simple rules engine. Meaning, not every problem needs an LLM. The contrast between the two projects illustrates the architectural judgement to reach for the right level of complexity.

**Key outcomes:** −98% mean time to assignment; −91% SLA breach rate; 35% more case volume absorbed in the 8 weeks post go-live with no headcount increase; team triage overhead reduced from ~40 engineer-hours per week to ~3.2.

---

### Project 3 — Multi-Tool Automation Orchestration

**Folder:** `Project-03-Multi-Tool-Orchestration/`

An end-to-end client onboarding pipeline that connects six systems (Google Form, Airtable, Claude API, SendGrid, Slack, and a Flask orchestration server) into a single webhook call that completes a full onboarding sequence in under three seconds. A new client submits a form; within seconds their CRM record is created, a personalised welcome email generated by Claude and delivered via SendGrid, their account manager alerted in Slack with a Block Kit message, and the CRM updated with delivery timestamps.

**What it demonstrates:** Systems orchestration thinking; connecting multiple platforms to solve a real business problem end-to-end. The central design is a step-runner pipeline engine (`pipeline.py`) that classifies each step as critical or non-critical, captures per-step timing and status, and returns a full pipeline trace on every call. A Slack failure never loses a client record or welcome email. A CRM failure halts everything. That distinction is made explicit in code, not left to chance.

**How it builds on Projects 1–2:** Inherits Project 1's Claude API integration pattern and Airtable client structure, then layers in four additional systems and the orchestration logic to coordinate them. The pipeline trace concept (step timing, outcome, partial success) reflects the operational maturity developed in Project 2's case study; observability matters before a system fails, not after.

**Key design decisions:** Sequential pipeline over parallel steps (simple trace, steps depend on previous results); critical vs non-critical step classification (explicit failure-mode reasoning); full pipeline trace on every call (immediate observability); Claude for email generation over a fixed template (genuine personalisation driven by `use_case` field); 201/207/502 HTTP status codes to signal success, partial success, and failure to the calling orchestrator.

---

### Project 4 — Power Automate + Microsoft 365 Integration

**Folder:** `Project-04-Power-Automate-M365/`

A scheduled Power Automate cloud flow that runs every Monday at 07:00 EST: retrieves compliance check items from SharePoint, validates required fields, filters to items requiring attention, sends the payload to an Azure Function that calls Claude to generate an executive summary, composes a full HTML report, writes an audit record, distributes via Outlook to the compliance distribution list, and posts a summary card to a Microsoft Teams channel. A Try/Catch scope pattern handles failures: errors are logged to SharePoint and a high-importance failure alert is sent to the same distribution list.

**What it demonstrates:** Depth on an enterprise platform. Power Automate is explicitly named in the job requirements, and this project builds a production-shaped flow (parameterised for environment promotion), with a dedicated service account, audit trail written before distribution begins, and the Anthropic API key never exposed to Power Automate. The Azure Function acts as the AI proxy, storing the key in encrypted Azure App Settings and returning structured JSON that the flow parses directly.

**How it builds on Projects 1–3:** The AI proxy pattern (Azure Function → Claude → structured JSON response) is the enterprise evolution of Project 1's direct Flask → Claude call. The audit trail written before distribution begins reflects the operational lesson from Project 2: make every run traceable regardless of outcome. The compliance check logic (filter → validate → summarise) mirrors the classification pipeline thinking from Project 3.

**Key design decisions:** Azure Function as AI proxy so the Anthropic API key never appears in Power Automate; audit record written before distribution (every run traceable even if the flow crashes mid-execution); AI receives only items with issues, capped at 30 (predictable token count, focused summaries); all environment-specific values as flow parameters (dev → UAT → prod promotion without rebuilding the flow); Try/Catch scope for structured error boundaries.

---

### Project 5 — AI Tool Evaluation Report

**Folder:** `Project-05-AI-Tool-Evaluation/`

A structured evaluation of Zapier, Make, and Power Automate for a defined business use case: client onboarding automation for a 20-person remote professional services firm on Google Workspace, with no in-house developer and a ~$100/month budget. Seven weighted criteria (AI integration depth 25%, cost 20%, ease of implementation 15%, reliability 15%, scalability 10%, ecosystem 10%, governance 5%) are scored against detailed per-platform assessments. A Python scoring model makes the methodology reproducible — any reader can change a weight or score and re-run. A sensitivity analysis confirms the recommendation holds across six alternative weight scenarios.

**What it demonstrates:** The ability to advise leadership — not just build. The evaluation is scenario-specific (not a general feature comparison), every score is justified with concrete evidence, and the recommendation includes a business justification, conditions under which to reconsider, an implementation path, and a risk register. The scoring model is a code artefact: `python src/scoring_model.py --sensitivity` regenerates every number in the report.

**How it builds on Projects 1–4:** The platforms being evaluated are the same platforms used to build the previous projects. The comparison of Make's HTTP module vs Zapier's Webhooks step for calling Claude (Project 5's highest-weighted criterion) is grounded in direct experience from Projects 1, 3, and 4 — not research. The Power Automate assessment draws on the Try/Catch scope pattern, parameter model, and Azure Function proxy architecture from Project 4.

**Recommendation:** Make (7.95/10 vs Power Automate 7.00 vs Zapier 6.75). The decision is driven by the two highest-weighted criteria: AI integration (Make's HTTP module handles Claude cleanly without code; Zapier requires JavaScript to parse the response) and cost (Make Core is $9/month; Zapier Professional is $73.50/month — a $780/year difference at equivalent capability). Power Automate would be the correct recommendation if the firm were on Microsoft 365.

---

## How the Projects Relate to Each Other

```
┌────────────────────────────────────────────────────────────────────┐
│  PROJECT 5: AI Tool Evaluation                                      │
│  (Advisory capstone — evaluates the platforms used in P1–P4        │
│   grounded in direct build experience, not theory)                  │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ evaluates
┌──────────────────────────▼─────────────────────────────────────────┐
│  PROJECT 4: Power Automate + Microsoft 365                          │
│  (Enterprise platform depth — Power Automate + Azure Functions      │
│   + SharePoint + Teams; AI proxy pattern; audit trail)             │
└──────────────────────────┬─────────────────────────────────────────┘
                           │ evolves AI + orchestration patterns from
┌──────────────────────────▼─────────────────────────────────────────┐
│  PROJECT 3: Multi-Tool Orchestration                                │
│  (Complexity step-up — 6 systems; step-runner pipeline engine;     │
│   critical vs non-critical failure handling; pipeline trace)        │
└───────────────┬──────────────────────────┬─────────────────────────┘
                │ inherits AI pattern from │ applies operational
                │                          │ thinking from
┌───────────────▼──────────┐  ┌────────────▼────────────────────────┐
│  PROJECT 1               │  │  PROJECT 2                           │
│  AI-Assisted Workflow    │  │  Process Optimisation Case Study     │
│  (Foundation: Claude +   │  │  (Strategy: AWS case study;          │
│   Flask + Airtable;      │  │   before/after process maps;         │
│   core AI integration    │  │   metrics; 3 ADRs; Python            │
│   pattern)               │  │   workflow simulator)                │
└──────────────────────────┘  └─────────────────────────────────────┘
```

Projects 1 and 2 are the foundation layer — one technical, one strategic. Project 1 establishes the AI integration pattern; Project 2 establishes the process architecture and decision-documentation discipline. Project 3 combines both: it uses the AI pattern from Project 1 and the operational thinking from Project 2, at greater system complexity. Project 4 takes those same patterns into an enterprise Microsoft environment, adding platform-specific depth. Project 5 closes the loop — evaluating the platforms used across the portfolio from an advisory perspective, with scores grounded in direct build experience.

---

## Common Technology Stack

| Layer | Technology |
|---|---|
| AI | Anthropic Claude (`claude-sonnet-4-6`) via Python SDK |
| Web framework | Python · Flask |
| Automation platforms | Zapier · Make · Microsoft Power Automate |
| CRM / data store | Airtable (REST API) |
| Email delivery | SendGrid (REST API) |
| Notifications | Slack (Incoming Webhooks · Block Kit) |
| Cloud functions | Azure Functions (Python v2 model) |
| Microsoft 365 | SharePoint · Outlook · Microsoft Teams |
| Environment config | python-dotenv · Azure App Settings (encrypted) |

Individual projects layer additional tools on top of this base — see each project's README for the full technology detail.

---

## Detailed Documentation

Each project folder contains a `README.md` with:

- Business problem and the operational context
- Architecture overview and system connections diagram
- Key design decisions with explicit rationale (the *why*, not just the *what*)
- Trade-offs: what each architectural choice gained and gave up
- What was learned: lessons that apply beyond this specific project
- Setup guide and, where applicable, runnable code or test suite

Navigate to the relevant folder to read the detailed documentation for any project.
