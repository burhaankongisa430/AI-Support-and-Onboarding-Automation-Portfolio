# Project 5 — AI Tool Evaluation Report

---

## Overview

This is the advisory capstone of the portfolio, a structured platform evaluation designed to show that an AI Automation Architect must also be able to advise leadership on which tools to invest in, why, and under what conditions that recommendation changes.

This evaluation compares **Zapier, Make, and Power Automate** for a defined real-world use case: client onboarding automation for a 20-person remote professional services firm. The evaluation is scenario-specific (not a general comparison), uses a weighted scoring model, and arrives at a recommendation with explicit business justification and a risk register.

---

## The Scenario

A 20-person B2B consulting firm on Google Workspace needs to automate client onboarding — 7 manual steps currently taking ~68 minutes per new client (~11 hours/month at current volume). The automation must include an AI-generated personalised welcome email, connect 6 apps (Google Sheets, HubSpot, Asana, Slack, Mailchimp, Claude API), and be maintainable by a non-developer. Budget: ~$100/month.

Full scenario definition: [evaluation/01-scenario.md](evaluation/01-scenario.md)

---

## Recommendation (summary)

**Build on Make.**

Make scores **7.95/10** vs Power Automate **7.00** vs Zapier **6.75** under the defined weighting.

The decision is driven primarily by the two highest-weighted criteria:
- **AI integration (25%):** Make's HTTP module handles Claude cleanly without code; Zapier requires JavaScript to parse the response
- **Cost (20%):** Make Core plan is $9/month; Zapier Professional is $73.50/month, a $780/year difference for equivalent capability at this volume

Make is also the most scalable choice for a growing firm that will add automation complexity over time.

Full recommendation and business justification: [evaluation/05-recommendation.md](evaluation/05-recommendation.md)

---

## How to Read This Project

Read the evaluation documents in order for the full reasoning chain:

| File | What it contains |
|---|---|
| [evaluation/01-scenario.md](evaluation/01-scenario.md) | Business context, current manual process, automation requirements |
| [evaluation/02-criteria.md](evaluation/02-criteria.md) | 7 scoring criteria with weights and justifications |
| [evaluation/03-platform-profiles.md](evaluation/03-platform-profiles.md) | Per-platform deep dive: capability, cost, limitations, evidence |
| [evaluation/04-comparison-matrix.md](evaluation/04-comparison-matrix.md) | Weighted scoring matrix, cost comparison, sensitivity test |
| [evaluation/05-recommendation.md](evaluation/05-recommendation.md) | Final recommendation with business justification and risk register |
| [diagrams/comparisons.md](diagrams/comparisons.md) | Mermaid charts: scores, costs, sensitivity, decision tree |
| [src/scoring_model.py](src/scoring_model.py) | Reproducible scoring model — run to regenerate all results |

---

## Running the Scoring Model

The scoring model requires no external dependencies — it runs on the Python standard library.

```bash
# Basic output — weighted totals and cost comparison
python src/scoring_model.py

# Markdown-formatted output (for pasting into documents)
python src/scoring_model.py --format markdown

# Include sensitivity analysis (tests recommendation under alternative weights)
python src/scoring_model.py --sensitivity
```

Example output:

```
=================================================================
  AI AUTOMATION PLATFORM EVALUATION
  Scenario: Client Onboarding — 20-person Remote Professional Services Firm
=================================================================

  RAW SCORES
  Criterion         Weight  Make  Power Automate  Zapier
  ──────────────────────────────────────────────────────
  Cost              20%     9     6               5
  Ease              15%     7     4               9
  Ai Integration    25%     8     7               6
  Reliability       15%     8     9               7
  Scalability       10%     8     9               6
  Ecosystem         10%     8     7               10
  Governance        5%      6     9               5

  WEIGHTED SCORE SUMMARY
  Platform        Total
  ─────────────────────
  Make            7.95
  Power Automate  7.00
  Zapier          6.75

=================================================================
  RECOMMENDATION: Make  (score: 7.95/10.00)
=================================================================
```

The model is intentionally transparent: change a raw score or weight in the source file and re-run to see the impact on the recommendation. The sensitivity analysis (`--sensitivity`) shows the recommendation holds across six alternative weight scenarios.

---

## Evaluation Methodology

### Scoring principles
- Scores are **scenario-specific**, not general product ratings
- Every score is justified with specific evidence in [evaluation/03-platform-profiles.md](evaluation/03-platform-profiles.md)
- Weights reflect the priorities of this specific organisation, not universal priorities
- The model is public and reproducible — any reader can challenge a score and see the effect

### Weight rationale (summary)
| Criterion | Weight | Why |
|---|---|---|
| AI integration | 25% | The AI email step is the highest-value, most-likely-to-evolve part of the workflow |
| Cost | 20% | Non-negotiable at a 20-person firm; $780/year is a meaningful budget line |
| Ease of implementation | 15% | No developer; ops team must own and maintain the automation |
| Reliability | 15% | Silent failures in client onboarding = client experience failures |
| Scalability | 10% | The firm is growing; platform choice should survive the next 2 years |
| Ecosystem | 10% | All 6 scenario apps must be native connectors |
| Governance | 5% | Baseline audit capability is adequate across all three; not a differentiator |

---

## Trade-offs

| Decision | What was gained | What was given up |
|---|---|---|
| Scenario-specific evaluation over general comparison | Actionable recommendation for a real decision | Results do not generalise to different organisation types (enterprise, M365 shops) |
| Weighted scoring over qualitative ranking | Reproducible; weight sensitivity testable | Weights are subjective; a different evaluator might weight criteria differently |
| 7 criteria over a shorter list | More nuanced; cost and AI integration captured separately | More complex; harder to communicate verbally to non-technical leadership |
| Make recommendation over Zapier | $780/year saving; better AI integration | Longer initial build time; higher learning curve for a non-technical user |

---

## What Was Learned

**The scenario definition is the most important document.** Before scoring any platform, the evaluation required a precisely defined business scenario — organisation size, tech stack, volume, budget, non-functional requirements. An evaluation without a scenario produces generic output that is useless for a real decision. Defining the scenario forces the evaluator to make the context explicit and prevents the evaluation from becoming a feature comparison sheet.

**Sensitivity analysis is a better presentation tool than it might seem.** Showing that Make wins under every tested weight scenario is more persuasive than showing it wins once. Stakeholders who disagree with the weighting can see that even if they prioritise their preferred criterion, the recommendation holds. It converts a potential objection ("but you weighted AI too high") into a verifiable claim ("if you change that weight, the result is X").

**Platform cost models are more different than they appear.** Zapier's task-based pricing and Make's operation-based pricing sound equivalent but behave very differently as workflows grow. Understanding the pricing mechanic, not just the headline price, is what produces an accurate cost comparison. An evaluator who only looks at headline prices would see $9 vs $29.99 vs $73.50 and miss the fact that Zapier's Starter plan runs out at 25 clients/month.
