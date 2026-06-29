# ADR-001 — Automation Approach: Rules Engine over ML Classifier

**Status:** Accepted
**Date:** 2024 (generalised)
**Context:** Internal case routing and escalation workflow automation

---

## Context

The team needed to classify incoming support cases into one of four priority tiers (P1–P4) based on the issue type and urgency signal provided at intake. Two approaches were considered:

1. A **rules-based engine** — explicit if/else logic mapping issue type and urgency to a tier
2. A **machine learning classifier** — trained on historical email data to predict the correct tier

---

## Decision

We chose the **rules-based engine**.

---

## Rationale

| Factor | Rules engine | ML classifier |
|---|---|---|
| Category space | 6 issue types → 4 tiers: small, well-defined | Would be solving a tractable but unnecessary complexity |
| Training data | Not needed | Required labelled historical cases — we had ~400 emails, all unstructured |
| Auditability | Every decision is traceable to a specific rule | Black-box predictions harder to explain to team leads |
| Maintenance | Rules changed by editing config; no retraining | Model drift requires monitoring and periodic retraining |
| Build time | ~1 day | Estimated 2–3 weeks including data labelling |
| Accuracy | 100% on well-formed input (deterministic) | Estimated 85–90% on clean text; lower on short/ambiguous descriptions |
| Edge case handling | Explicit promotion logic for urgency signal mismatch | Model would have learned implicit patterns that may not generalise |

The decisive factor was the **structured intake form**. Once we committed to a form (rather than free-form email), the classification inputs were guaranteed to be clean and categorical. The problem no longer required any natural language understanding — and applying ML to a problem that can be solved with a lookup table is the wrong level of complexity.

---

## Consequences

**Positive:**
- Classification is deterministic and fully auditable
- No training data required; no model lifecycle to manage
- Any engineer can read and modify the rules without ML expertise
- Zero false positives in production

**Negative:**
- Adding a new issue type requires a code/config change and deployment (not a model retrain)
- Does not generalise to free-form text input without a parsing layer
- Cannot learn from edge cases over time without explicit rule updates

---

## Revisit trigger

If the intake mechanism is ever changed back to free-form email or the category taxonomy expands beyond ~10 types with significant overlap, revisit this decision and evaluate a lightweight text classifier (e.g. zero-shot classification via a small LLM) at that point.

---

# ADR-002 — SLA Enforcement: Polling over Event Timers

**Status:** Accepted
**Date:** 2024 (generalised)

---

## Context

Once a case is assigned and an SLA deadline recorded, the system needs to send proactive notifications before breach and escalation alerts at breach. Two approaches were considered:

1. **Event-based timers** — schedule a timed event at `created_at + sla_minutes * 0.8` for the nudge and `created_at + sla_minutes` for the escalation
2. **Polling job** — a scheduled job runs every 15 minutes and queries all open cases against the current time

---

## Decision

We chose the **polling job (15-minute interval)**.

---

## Rationale

| Factor | Polling | Event timers |
|---|---|---|
| Reliability on restart | Idempotent — poll recalculates state from DB on every run | Timer state lost on restart unless persisted separately |
| Missed notifications | None — every run checks all open cases | A timer that fires during a deployment window is silently dropped |
| Operational complexity | Single scheduled job, one query | N timers in flight at any time (N = number of open cases) |
| Observability | One job to monitor; logs every run | Hard to tell which timers are in flight without dedicated timer state |
| Latency | Max 15-min delay between breach and notification | Fires at exactly the right time |

For the SLA tiers in use (shortest: 15 min for P1), a maximum 15-minute polling delay meant a P1 escalation could arrive up to 30 minutes after breach in the worst case (breach at minute 0 of a polling cycle, nudge sent at minute 15, escalation at minute 30). This was considered acceptable given P1 cases also triggered immediate assignee notification on intake.

---

## Consequences

**Positive:**
- Zero missed notifications across production runtime
- System survived multiple restarts and deployments without state loss
- Easy to monitor: one log line per run, one alert if the job fails to run

**Negative:**
- P1 escalation latency up to 30 minutes past breach (mitigated by intake notification)
- Polling adds minor load on the data store every 15 minutes

---

## Revisit trigger

If SLA tiers are tightened below 15 minutes, switch to event-driven timers with a persistent timer store (e.g. a scheduled message in a queue with visibility timeout).

---

# ADR-003 — Intake Mechanism: Structured Form over Free-Form Email

**Status:** Accepted
**Date:** 2024 (generalised)

---

## Decision

Replace the free-form email alias as the primary intake channel with a mandatory structured web form for all new cases.

---

## Rationale

The single highest-leverage architectural decision in this project. Free-form email intake created downstream complexity at every step: classification required text parsing, assignment had no reliable urgency signal, and tracking had no structured data to write. By enforcing structure at the point of entry, all downstream components became simpler, faster to build, and more reliable.

The user experience cost was considered: requiring a form instead of an email is a higher-friction intake. This was mitigated by keeping the form short (6 fields, ~2 minutes to complete) and embedding it prominently in the internal developer portal where the affected tools were already documented.

---

## Consequences

**Positive:**
- Classification accuracy: 100% (rules engine has clean categorical inputs)
- No NLP or text parsing required anywhere in the pipeline
- Structured data available for reporting from day one

**Negative:**
- Requesters who preferred email had to change their habit
- Requires form maintenance as the tool catalogue evolves
- Does not capture cases raised via other channels (e.g. Slack messages to team members)
