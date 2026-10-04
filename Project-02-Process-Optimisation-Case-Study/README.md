# Project 2 — Process Optimisation Case Study

---

## Overview

This case study documents a real workflow automation initiative contributed to during employment at a large cloud services organisation (generalised to protect confidential information). The initiative automated the manual intake, classification, routing, and SLA enforcement process for an internal developer tooling support team.

The project required no AI model. Instead, it demonstrates **architect-level process thinking**: identifying the right level of complexity for a given problem, designing a solution that actually changes operational behaviour, and measuring the impact rigorously.

---

## The Problem in One Sentence

A team of 8 engineers was spending ~40 hours per week on inbox triage, manual assignment, spreadsheet updates, and reactive escalation; time that was entirely recoverable through automation, with measurable SLA improvement as the outcome.

---

## Results at a Glance

| Metric | Before | After |
|---|---|---|
| Mean time to first assignment | 3 h 47 min | < 1 second |
| SLA breach rate | 34% | 3% |
| Engineer triage overhead / week | ~40 h (team) | ~3.2 h (team) |
| Duplicate-handling incidents / week | ~6 | 0 |
| Case volume absorbed without headcount increase | 110/week | 148/week (+35%) |

---

## What Was Built

Three automation components working together:

1. **Structured intake form** — replaced free-form email; guaranteed clean, categorical data at the point of entry
2. **Classification and assignment engine** — rules-based tier assignment (P1–P4) with round-robin engineer routing, collision-free
3. **SLA watcher** — polling job that ran every 15 minutes, sending proactive nudges at 80% of SLA elapsed and escalations at breach

---

## How to Read This Project

| File | What it shows |
|---|---|
| [case-study.md](case-study.md) | Full written narrative: problem, approach, decisions, results, lessons |
| [diagrams/before-state.md](diagrams/before-state.md) | Mermaid process map of the manual workflow with annotated pain points |
| [diagrams/after-state.md](diagrams/after-state.md) | Mermaid process map of the automated workflow with comparison table |
| [diagrams/architecture.md](diagrams/architecture.md) | Technical component architecture + data schema |
| [decisions/adr-001-automation-platform.md](decisions/adr-001-automation-platform.md) | Three Architecture Decision Records: rules vs ML, polling vs timers, form vs email |
| [metrics/impact-summary.md](metrics/impact-summary.md) | Full before/after metric breakdown with confidence notes |
| [src/workflow_simulator.py](src/workflow_simulator.py) | Runnable Python code demonstrating all three automation components |

Start with [case-study.md](case-study.md) for the narrative, then use the diagrams and ADRs for depth.

---

## Running the Simulator

The simulator requires no API keys or external dependencies — it runs on the Python standard library.

```bash
python src/workflow_simulator.py
```

This processes 6 sample cases through the full pipeline and prints:
- Intake routing output (tier, assignee, SLA deadline)
- SLA watcher simulation across 5 time checkpoints
- Before/after metric comparison table

Example output:

```
=================================================================
  CASE ROUTING & SLA TRACKING — WORKFLOW SIMULATOR
=================================================================

--- INTAKE & ROUTING ---

  CASE-A3F1C2  P1 Critical      assignee=alice    SLA=  15 min  deploy-accelerator
  [NOTIFY] alice assigned CASE-A3F1C2 (P1 Critical) — SLA deadline 14:32 UTC
  CASE-B7D4E1  P2 High          assignee=alice    SLA=  60 min  etl-runner
  ...

--- SLA WATCHER SIMULATION ---

  T+  15min — checked 6 open cases  nudges=1  escalations=1
  T+  60min — checked 5 open cases  nudges=2  escalations=1
  ...
```

---

## Key Architectural Insight

The most impactful decision in this project was not the automation logic — it was enforcing a **structured intake form** over free-form email. Once the input was structured, downstream components became trivially simple. This reflects a core principle in automation architecture: **complexity compounds downstream from poor input design**. Fix the input, and most of the problem disappears.

---

## Trade-offs

| Decision | What was gained | What was given up |
|---|---|---|
| Rules engine over ML | Deterministic, auditable, zero false positives | Cannot adapt to new patterns without code changes |
| Polling over event timers | Operationally stable across restarts | Max 15-min delay between breach and escalation for P1 |
| Structured form over email | 100% input quality; no NLP needed | Higher friction for requesters; requires form maintenance |
| Relational data store over spreadsheet | Real-time querying, aggregation, dashboard | Migration effort; requires DB access for ad-hoc queries |

---

## What Was Learned (Key Takeaway)

**Making data visible changes behaviour independent of automation.** Within the first week of the live SLA dashboard, engineers were self-managing their queues more proactively — not because the automation forced them to, but because they could now see their own SLA health in real time. Observability is itself an intervention, not just a diagnostic tool.

See [case-study.md § 6](case-study.md#6-what-was-learned) for the full set of lessons.
