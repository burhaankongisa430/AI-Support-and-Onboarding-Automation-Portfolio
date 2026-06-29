# Case Study — Internal Case Routing & Escalation Workflow Automation

**Organisation type:** Large cloud services organisation — internal developer tooling team
**Author:** Burhaan Mziwakhe Kongisa
**Role during project:** Workflow Automation Contributor, Tool Builders Team
**Note:** All system names and team identifiers have been generalised to protect confidential information.

---

## 1. Context

The internal developer tooling team ("Tool Builders") supported hundreds of internal engineering teams that relied on a shared library of build tools, deployment accelerators, and operational scripts. When an engineering team encountered a problem — a broken tool, an unexpected behaviour, a configuration question — they raised a case via an email alias.

The team handling these cases had no intake system, no prioritisation logic, and no SLA visibility. Everything lived in a shared inbox.

---

## 2. The Problem

### Before-state summary

At the start of this initiative, the case handling process was entirely manual:

1. A case arrived in a shared email inbox watched by the whole team
2. The first available person read the email, made a judgement call on urgency, and self-assigned it
3. Assignment was communicated by replying-all so others would know to skip it
4. There was no classification — billing queries, tool defects, integration failures, and general questions all arrived in the same queue with no visual differentiation
5. Escalation happened when someone noticed an old email that had not been replied to
6. Progress and resolution were tracked in a shared spreadsheet, updated manually and inconsistently

### Observed pain points

| Pain point | Impact |
|---|---|
| Double-handling — two people starting work on the same case | Wasted effort; confusion for the requestor receiving two responses |
| No urgency signal at intake | Production-blocking cases sat in queue alongside low-priority queries |
| Manual spreadsheet tracking | Data was stale within hours; no one trusted the numbers |
| Escalation by memory | SLA breaches discovered retrospectively, not proactively |
| No structured data | Impossible to report on case volume, category mix, or resolution time |

### Baseline metrics (measured over 8 weeks prior to automation)

| Metric | Baseline |
|---|---|
| Mean time to first assignment | 3 h 47 min |
| SLA breach rate (4-hour first response) | 34% |
| Cases per week | ~110 |
| Time spent on triage and tracking per engineer per week | ~4.5 hours |
| Duplicate-handling incidents per week | ~6 |

---

## 3. The Automation Approach

### Goal

Replace the manual intake-and-triage loop with an automated pipeline that classifies incoming cases, assigns them to the right engineer, tracks SLAs in real time, and escalates proactively — without requiring engineers to police a shared inbox.

### What was built

A lightweight automation layer on top of the existing email alias, integrating three components:

**Component 1 — Structured intake form**
The email alias was supplemented with a mandatory intake form (replacing free-form email for new cases). The form captured: requester name, team, tool name, issue type (dropdown), urgency self-assessment, and a free-text description. This gave every case a structured starting point.

**Component 2 — Automated classification and routing**
An automation workflow (built on an internal task orchestration platform) triggered on each new form submission. It applied a rules-based classification engine — cross-referencing the issue type, affected tool, and urgency signal — to assign:
- A **priority tier** (P1 Critical / P2 High / P3 Medium / P4 Low)
- An **owning engineer** (round-robin within tier-appropriate subgroups)
- A **response SLA target** (15 min / 1 h / 4 h / 8 h)

The assigned engineer received a structured notification with all context pre-populated — no inbox scanning required.

**Component 3 — SLA tracking and proactive escalation**
A scheduled job ran every 15 minutes, comparing the current time against each open case's SLA deadline. Cases within 20% of their deadline with no response triggered an automated nudge to the assignee. Cases that breached their SLA triggered an escalation notification to the team lead, with the case context attached.

All case state was written to a central data store (replacing the manual spreadsheet), with a live dashboard showing queue depth, SLA health, and category distribution.

### Automation flow (after-state)

```
Form submission
    → Webhook triggers classification engine
    → Priority tier + assignee + SLA deadline calculated
    → Case record created in central data store
    → Assignee notified with full context
    → SLA watcher job checks every 15 minutes
        → Nudge at 80% of SLA elapsed
        → Escalation at 100% (breach)
    → On resolution: case closed, metrics recorded
```

---

## 4. Architectural Decisions

See [decisions/adr-001-automation-platform.md](decisions/adr-001-automation-platform.md) for the detailed record.

**Summary of key decisions:**

| Decision | Choice made | Reason |
|---|---|---|
| Intake mechanism | Structured form over free-form email | Guarantees structured data at the point of entry; no NLP parsing needed |
| Classification approach | Rules-based engine over ML model | The category space was small and well-defined; a rules engine was deterministic, auditable, and required no training data |
| Assignment algorithm | Round-robin with tier-based subgroups over manual assignment | Eliminated the self-assign race condition; distributed load evenly |
| SLA tracking | Polling job (15 min interval) over event-driven timers | Simpler to build and debug; 15-minute granularity was sufficient for the SLA tiers in use |
| Data store | Relational table over continuing to use the spreadsheet | Enabled reliable querying, aggregation, and dashboard connectivity |

---

## 5. Results (measured over 8 weeks after go-live)

| Metric | Before | After | Change |
|---|---|---|---|
| Mean time to first assignment | 3 h 47 min | 4 min | **-98%** |
| SLA breach rate | 34% | 3% | **-91%** |
| Duplicate-handling incidents / week | ~6 | 0 | **-100%** |
| Triage + tracking time / engineer / week | 4.5 h | 0.4 h | **-91%** |
| Reportable case volume (accurate) | ~60% accurate | ~99% accurate | **+65%** |
| Cases per week (capacity now visible) | 110 | 110 → 148* | *+35% capacity absorbed without headcount increase* |

> *Case volume grew 35% in the 8 weeks following go-live, partially because the new form made it easier to raise cases. The team handled the increase without adding headcount — the time recovered from manual triage was redirected to resolution.

---

## 6. What Was Learned

**Rules over models at small scale.** The initial design considered an ML classifier to categorise cases. During scoping it became clear that the category taxonomy had only 6 values, all well-defined, and that the structured intake form already gave a clean `issue_type` signal. A rules engine was faster to build, easier to audit, and produced no false positives. The lesson: reach for a rules engine before an ML model when the decision space is small and structured input is available.

**Garbage-in at intake ruins everything downstream.** The first prototype accepted free-form email because changing the intake channel felt like asking too much of users. The result was that classification accuracy was poor and assignment logic had to handle too many edge cases. Switching to a structured form was the single highest-leverage change in the project — not the automation logic itself.

**SLA visibility changes behaviour before the automation does.** Within the first week of the live dashboard, engineers began self-managing their queue more proactively — not because they were told to, but because they could now see their own SLA health in real time. The act of making the data visible produced a behavioural shift independent of the automated escalation logic.

**Scheduled polling is more operationally stable than event timers for SLA enforcement.** An earlier design used time-based event triggers (fire a notification exactly N minutes after assignment). These were fragile — a system restart or deployment during a trigger window could silently drop a notification. The polling job checked every 15 minutes and was idempotent by design, so restarts caused no missed escalations.

---

## 7. Generalisation Note

This case study describes work contributed to during employment with a large cloud services organisation. All internal system names, team identifiers, tooling names, and proprietary process details have been generalised or omitted. The workflow patterns, metrics, and architectural decisions described are real but have been anonymised to avoid disclosing confidential operational information.
