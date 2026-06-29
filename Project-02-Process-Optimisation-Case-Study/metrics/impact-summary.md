# Impact Summary — Case Routing Automation

**Measurement period:** 8 weeks pre-automation vs. 8 weeks post-go-live
**Team size:** 8 engineers
**Average case volume:** ~110 cases/week (pre); ~148 cases/week (post)

---

## Primary Metrics

| Metric | Before | After | Change |
|---|---|---|---|
| Mean time to first assignment | 3 h 47 min | < 1 second | **-98%** |
| SLA breach rate (4h first response) | 34% | 3% | **-91%** |
| Duplicate-handling incidents / week | ~6 | 0 | **-100%** |
| Cases handled / week | 110 | 148 | **+35%** *(no headcount increase)* |

---

## Efficiency Metrics

| Metric | Before | After | Change |
|---|---|---|---|
| Engineer triage time / week (team total) | ~36 h | ~3.2 h | **-91%** |
| Engineer tracking time / week (team total) | ~4 h | ~0 h | **-100%** |
| Total non-resolution overhead / week | ~40 h | ~3.2 h | **-92%** |
| Hours recovered / engineer / week | — | ~4.6 h | **+4.6 h/eng/week** |

> The 4.6 hours recovered per engineer per week was redirected to case resolution.
> This is the primary reason the team absorbed a 35% volume increase without hiring.

---

## Data Quality Metrics

| Metric | Before | After | Change |
|---|---|---|---|
| Case records with complete data | ~60% | ~99% | **+65pp** |
| Spreadsheet update lag (typical) | 2–6 hours | Real-time | Eliminated |
| Cases with category recorded | ~40% | 100% | **+60pp** |
| Dashboard data freshness | Next-day manual | 5-min polling | **-99% lag** |

---

## Escalation Metrics

| Metric | Before | After |
|---|---|---|
| Escalations discovered reactively (after breach) | 100% | 0% |
| Escalations triggered proactively (before breach) | 0% | 100% |
| Average time between breach and team lead awareness | 3.2 h | < 15 min |

---

## Weekly Time Recovery (Illustration)

```
Before automation — 110 cases/week, 8 engineers:
    Triage (read, classify, assign): ~20 min × 110 = 36.7 h
    Tracking (spreadsheet updates):  ~2 min  × 110 =  3.7 h
    Escalation coordination:         ~5 min  × 6   =  0.5 h
    ─────────────────────────────────────────────────────────
    Total overhead/week:                              40.9 h
    Overhead per engineer:                             5.1 h

After automation — 148 cases/week, 8 engineers:
    Review assignee notification:    ~30 s   × 148 =  1.2 h
    Resolve anomalies / edge cases:  manual  × ~8   =  2.0 h
    ─────────────────────────────────────────────────────────
    Total overhead/week:                               3.2 h
    Overhead per engineer:                             0.4 h

Net recovered per engineer per week:                   4.7 h
Net recovered across team per week:                   37.7 h
```

---

## Confidence Notes

- Baseline metrics sourced from 8-week retrospective analysis of the shared inbox and manual spreadsheet (data completeness ~60%, so baseline figures carry ±15% uncertainty)
- Post-automation metrics sourced from automated case records (data completeness ~99%)
- SLA breach rate calculated as: cases where `first_response_at - created_at > sla_deadline - created_at`, divided by total cases
- "Duplicate-handling incidents" counted from inbox thread analysis pre-automation; post-automation verified by `assignee` column uniqueness per case
