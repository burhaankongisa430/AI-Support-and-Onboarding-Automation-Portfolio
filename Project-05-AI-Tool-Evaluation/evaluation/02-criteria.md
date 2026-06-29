# Scoring Criteria & Weighting

## Methodology

Each platform is scored on a **1–10 scale** across seven criteria. Scores reflect performance specifically in the context of the defined scenario (see [01-scenario.md](01-scenario.md)) — a 20-person remote professional services firm automating client onboarding with AI-generated email, no in-house developer, and a ~$100/month budget.

A score of **10** means the platform is an excellent fit for this criterion in this context.
A score of **1** means the platform is a poor fit or actively introduces problems.

Scores are intentionally scenario-specific. A score of 4 on "ease of use" for Power Automate does not mean Power Automate is a bad product — it means it is the hardest of the three to operate without developer support, in the context of a non-technical team.

---

## Criteria

### 1. Cost at SME Scale — Weight: 20%

**What is measured:** Total monthly platform cost for the defined scenario at realistic SME volume (~150 automation runs per month — 10 new clients × 15 steps per pipeline). Includes base plan cost, per-task/operation charges, and any add-ons needed for AI integration or app connectors.

**Why 20%:** For a 20-person firm, every recurring SaaS cost is scrutinised. A platform that is technically superior but costs 4× as much at this volume is not the right tool for this client.

**Scoring guide:**
- 9–10: Under $25/month total at this volume with room to grow
- 7–8: $25–60/month — manageable for a professional services firm
- 5–6: $60–100/month — at the upper limit of the stated budget
- 3–4: $100–150/month — exceeds budget without clear justification
- 1–2: Over $150/month or unpredictable/usage-based costs

---

### 2. Ease of Implementation — Weight: 15%

**What is measured:** How quickly and confidently a non-developer operations professional can build, test, and modify this specific workflow. Includes time to first working automation, clarity of the builder UI, quality of error messages, and maintainability by someone who did not originally build it.

**Why 15%:** The firm has no developer. If the automation breaks six months after a consultant built it, the ops team must be able to debug and fix it. Platforms that require code or deep technical knowledge to modify create a dependency.

**Scoring guide:**
- 9–10: A non-technical ops person can build and maintain this independently
- 7–8: Requires initial setup guidance but ops can maintain it after training
- 5–6: Non-technical person can follow it but needs developer help for changes
- 3–4: Effectively requires a developer to build and maintain
- 1–2: Developer-only tooling at this level of complexity

---

### 3. AI Integration Depth — Weight: 25%

**What is measured:** How well the platform supports calling an AI API (OpenAI, Anthropic Claude, or similar) to generate content — specifically the personalised welcome email in this scenario. Includes native AI connectors, HTTP flexibility, prompt configuration, response parsing, and ability to pass dynamic context (client name, industry, use case) into the AI call.

**Why 25%:** The AI-generated welcome email is the highest-value step in this workflow and the one most likely to evolve (new models, new prompt strategies, additional AI steps). A platform that handles AI integration poorly makes the most valuable part of the automation brittle.

**Scoring guide:**
- 9–10: Native AI connectors or clean HTTP with full JSON control; dynamic context injection; response parsing built-in
- 7–8: HTTP action available; some configuration needed but straightforward; parsing requires a step or two
- 5–6: AI integration possible but cumbersome; limited by connector restrictions or output parsing difficulty
- 3–4: AI requires a workaround (e.g. Zapier Code step with JavaScript knowledge)
- 1–2: No practical path to AI integration without developer involvement

---

### 4. Reliability & Error Handling — Weight: 15%

**What is measured:** What happens when a step fails. Does the platform retry automatically? Does it notify someone? Is the failure visible and diagnosable? Can the team tell which step failed and why, without digging through logs?

**Why 15%:** Automation that fails silently is worse than no automation — it creates the illusion that something happened when it didn't. For client onboarding, a missed welcome email or CRM record is a client experience failure. The platform must surface failures clearly.

**Scoring guide:**
- 9–10: Per-step error handling; automatic retry with config; clear failure notifications; run history with step-level visibility
- 7–8: Email alert on failure; some retry; run history visible
- 5–6: Basic failure notification; limited retry; diagnosis requires navigating the platform
- 3–4: Failure notification available but not default; limited visibility
- 1–2: Silent failures possible; no built-in error alerting

---

### 5. Scalability — Weight: 10%

**What is measured:** How well the platform grows with the business — both in volume (from 10 to 50+ new clients/month) and in complexity (from one workflow to a dozen interconnected ones). Includes pricing model at higher volumes and whether complex logic (branching, loops, sub-processes) is supported.

**Why 10%:** The firm is growing. The automation built today should not need to be rebuilt in 18 months. However, scalability is weighted lower than cost and AI because at 20 people today, the near-term scenario is more important than a hypothetical future state.

**Scoring guide:**
- 9–10: Pricing scales linearly or better; supports complex multi-branch logic; scenario is a small fraction of capability
- 7–8: Scales well for typical SME growth; some limitations on complexity
- 5–6: Adequate for current scale; meaningful rebuild or cost jump at 3–5× volume
- 3–4: Hits limits at moderate growth; pricing becomes prohibitive
- 1–2: Not designed for this kind of scaling

---

### 6. Ecosystem & App Connectors — Weight: 10%

**What is measured:** Whether the platform has native connectors for the apps in this scenario: Google Workspace, HubSpot, Asana, Slack, Mailchimp, Stripe. Native connectors are lower friction, more reliable, and easier to maintain than HTTP-based workarounds.

**Why 10%:** The scenario covers 6 apps. A platform with all 6 as native connectors is meaningfully easier to build and maintain than one where 2 of them require custom HTTP calls.

**Scoring guide:**
- 9–10: All 6 scenario apps available as maintained native connectors
- 7–8: 5 of 6 apps native; one requires HTTP or a workaround
- 5–6: 4 of 6 native; acceptable but adds friction
- 3–4: Only 3 of 6 native; significant build overhead
- 1–2: Fewer than 3 native connectors for this scenario

---

### 7. Governance & Auditability — Weight: 5%

**What is measured:** Whether the platform provides run history, audit logs, access controls (who can edit the automation), and version history. For a professional services firm, being able to answer "did the onboarding automation run for client X on date Y?" is a business requirement.

**Why 5%:** Important but not a differentiator at this scale. All three platforms provide some form of run history. The weight is low because the baseline is acceptable across the board, and the differences don't materially affect the recommendation for a 20-person firm.

**Scoring guide:**
- 9–10: Full run history with step-level detail; version control; role-based access
- 7–8: Run history with some step visibility; basic access control
- 5–6: Run history exists; limited step-level detail; limited access control
- 3–4: Minimal run history; limited governance
- 1–2: No meaningful audit capability

---

## Weight Summary

| Criterion | Weight | Rationale |
|---|---|---|
| Cost at SME scale | 20% | Non-negotiable at this firm size |
| Ease of implementation | 15% | No developer; ops team must own it |
| AI integration depth | 25% | AI email is the highest-value step |
| Reliability & error handling | 15% | Silent failures = client experience failures |
| Scalability | 10% | Growth matters but future-proofing is secondary to today |
| Ecosystem & connectors | 10% | 6 specific apps; native support matters |
| Governance & auditability | 5% | Baseline acceptable; not a differentiator |
| **Total** | **100%** | |
