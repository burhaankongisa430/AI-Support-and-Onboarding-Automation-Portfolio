# Comparison Matrix — Weighted Scoring

## Raw Scores (1–10)

Scores reflect performance specifically in the context of the [defined scenario](01-scenario.md):
a 20-person remote professional services firm automating client onboarding, on Google Workspace,
with no in-house developer. Full scoring rationale in [03-platform-profiles.md](03-platform-profiles.md).

| Criterion | Weight | Zapier | Make | Power Automate |
|---|---|---|---|---|
| Cost at SME scale | 20% | 5 | **9** | 6 |
| Ease of implementation | 15% | **9** | 7 | 4 |
| AI integration depth | 25% | 6 | **8** | 7 |
| Reliability & error handling | 15% | 7 | 8 | **9** |
| Scalability | 10% | 6 | 8 | **9** |
| Ecosystem & connectors | 10% | **10** | 8 | 7 |
| Governance & auditability | 5% | 5 | 6 | **9** |

---

## Weighted Scores

| Criterion | Weight | Zapier | Make | Power Automate |
|---|---|---|---|---|
| Cost at SME scale | 20% | 1.00 | **1.80** | 1.20 |
| Ease of implementation | 15% | **1.35** | 1.05 | 0.60 |
| AI integration depth | 25% | 1.50 | **2.00** | 1.75 |
| Reliability & error handling | 15% | 1.05 | 1.20 | **1.35** |
| Scalability | 10% | 0.60 | 0.80 | **0.90** |
| Ecosystem & connectors | 10% | **1.00** | 0.80 | 0.70 |
| Governance & auditability | 5% | 0.25 | 0.30 | **0.45** |
| **Total** | **100%** | **6.75** | **7.95** | **7.00** |

---

## Score Visualisation

```
Platform             Score   Visual
─────────────────────────────────────────────────────────────
Make                  7.95   ████████████████████████████████▌
Power Automate        7.00   ████████████████████████████
Zapier                6.75   ███████████████████████████
                             0    2    4    6    8    10
```

---

## Per-Criterion Winner

| Criterion | Winner | Margin |
|---|---|---|
| Cost at SME scale | **Make** | Make 1.80 vs PA 1.20 vs Zapier 1.00 |
| Ease of implementation | **Zapier** | Zapier 1.35 vs Make 1.05 vs PA 0.60 |
| AI integration depth | **Make** | Make 2.00 vs PA 1.75 vs Zapier 1.50 |
| Reliability & error handling | **Power Automate** | PA 1.35 vs Make 1.20 vs Zapier 1.05 |
| Scalability | **Power Automate** | PA 0.90 vs Make 0.80 vs Zapier 0.60 |
| Ecosystem & connectors | **Zapier** | Zapier 1.00 vs Make 0.80 vs PA 0.70 |
| Governance & auditability | **Power Automate** | PA 0.45 vs Make 0.30 vs Zapier 0.25 |

**Make wins 2 of the top 3 weighted criteria** (cost and AI integration, together 45% of total weight), which explains its overall lead despite Power Automate winning more individual criteria at lower weights.

---

## Cost Comparison

Monthly cost for the defined scenario at current volume (10 clients/month):

| Plan | Zapier | Make | Power Automate |
|---|---|---|---|
| Entry-level adequate plan | Professional ($73.50/mo) | Core ($9/mo) | Premium ($15/user/mo × 2 = $30/mo) |
| Operations/tasks included | 2,000 tasks | 10,000 ops | Unlimited (connector-limited) |
| Scenario operations used/mo | ~90 tasks | ~90 ops | ~90 actions |
| Headroom at current volume | 22× | 111× | N/A |
| Cost at 5× volume (50 clients) | $73.50 (still adequate) | $9 (still adequate) | $30 (still adequate) |
| Cost at 20× volume (200 clients) | ~$200+ (5k task plan) | $16 (Pro plan) | $30+ (scales with users not volume) |
| **Effective cost today** | **$73.50/mo** | **$9/mo** | **$30/mo** |

> Note: The Zapier Starter plan ($29.99/mo) is technically adequate today at 90 tasks/month but
> provides very little growth headroom. Professional is the realistic starting point for a firm
> expecting to grow.

---

## Scenario-Specific Observations

**Where Make wins decisively:**
The two highest-weighted criteria (AI integration, 25%; cost, 20%) are both won by Make. The $64.50/month cost advantage over Zapier and the cleaner Claude integration path are not marginal differences — they are material for a 20-person firm making a long-term tool choice.

**Where Zapier is genuinely better:**
Ease of implementation is real and matters for the first build. If the operations team needs a working automation in 48 hours with no training, Zapier is the right call today. The connector breadth is also a genuine advantage — if the firm adds a new tool, Zapier's 6,000 connectors are more likely to cover it natively.

**Where Power Automate would be the answer:**
If this firm ran Microsoft 365 (Teams, SharePoint, Outlook, OneDrive), Power Automate's connector advantage would flip the score substantially. The reliability and governance scores would also carry more weight in a regulated environment or a firm with compliance requirements. None of these conditions apply here.

**The sensitivity test:**
If AI integration weight is reduced from 25% to 15% (and cost raised from 20% to 30%):
- Make: 8.05
- Power Automate: 6.80
- Zapier: 6.35

Make wins regardless. The recommendation is robust to reasonable weight changes.
