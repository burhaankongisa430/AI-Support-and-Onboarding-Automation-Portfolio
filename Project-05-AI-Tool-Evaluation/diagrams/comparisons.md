# Visual Comparisons

## Overall Weighted Scores

```mermaid
xychart-beta
    title "Overall Weighted Score (out of 10)"
    x-axis ["Make", "Power Automate", "Zapier"]
    y-axis "Score" 0 --> 10
    bar [7.95, 7.00, 6.75]
```

---

## Score by Criterion

```mermaid
xychart-beta
    title "Raw Scores by Criterion — Zapier vs Make vs Power Automate"
    x-axis ["Cost", "Ease", "AI Integration", "Reliability", "Scalability", "Ecosystem", "Governance"]
    y-axis "Score (1-10)" 0 --> 10
    bar [5, 9, 6, 7, 6, 10, 5]
    bar [9, 7, 8, 8, 8, 8, 6]
    bar [6, 4, 7, 9, 9, 7, 9]
```

*Bars left-to-right: Zapier · Make · Power Automate*

---

## Monthly Cost Comparison

```mermaid
xychart-beta
    title "Monthly Platform Cost (USD) — Current Volume vs 20× Growth"
    x-axis ["Current (~150 runs/mo)", "5× Volume (~750 runs/mo)", "20× Volume (~3000 runs/mo)"]
    y-axis "Monthly Cost (USD)" 0 --> 220
    line [73.50, 73.50, 199.00]
    line [9.00, 9.00, 16.00]
    line [30.00, 30.00, 30.00]
```

*Lines top-to-bottom at 20× volume: Zapier · Power Automate · Make*

---

## Criterion Weight Distribution

```mermaid
pie title Evaluation Criterion Weights
    "AI Integration (25%)" : 25
    "Cost at SME Scale (20%)" : 20
    "Ease of Implementation (15%)" : 15
    "Reliability & Error Handling (15%)" : 15
    "Scalability (10%)" : 10
    "Ecosystem & Connectors (10%)" : 10
    "Governance & Auditability (5%)" : 5
```

---

## Platform Fit for This Scenario

```mermaid
quadrantChart
    title Platform Fit — Cost Efficiency vs AI Integration Quality
    x-axis Low AI Integration --> High AI Integration
    y-axis High Cost --> Low Cost
    quadrant-1 "Best fit: low cost + strong AI"
    quadrant-2 "Easy entry but AI limited"
    quadrant-3 "Expensive and AI limited"
    quadrant-4 "Powerful AI but expensive"
    Make: [0.75, 0.85]
    Zapier: [0.55, 0.30]
    Power Automate: [0.65, 0.55]
```

---

## Sensitivity Analysis — Does the Winner Change?

```mermaid
xychart-beta
    title "Sensitivity Analysis — Total Score Under Alternative Weight Scenarios"
    x-axis ["Base", "Cost +10%", "AI +10%", "Ease +10%", "Governance +10%", "Reliability +10%"]
    y-axis "Weighted Total" 6 --> 9
    line [6.75, 6.35, 6.25, 7.10, 6.20, 6.65]
    line [7.95, 8.05, 8.45, 7.55, 7.80, 7.85]
    line [7.00, 6.85, 7.15, 6.25, 7.55, 7.30]
```

*Lines: Zapier · Make · Power Automate*

**Make leads in every scenario tested.** The recommendation is robust to reasonable weight changes.

---

## Decision Tree — Platform Selection

```mermaid
flowchart TD
    A{Is the firm on\nMicrosoft 365?} -->|Yes| B{Are there enterprise\ncompliance requirements?}
    A -->|No| C{Is the automation\nneeded in < 72 hours?}

    B -->|Yes| D[Power Automate\nEnterprise governance + M365 depth]
    B -->|No| E{Budget > $100/mo?}
    E -->|Yes| D
    E -->|No| F[Make\nBest value even in M365 context]

    C -->|Yes| G[Zapier\nFastest to first working automation]
    C -->|No| H{Is AI integration\na primary requirement?}
    H -->|Yes| I[Make\nClearest Claude integration path]
    H -->|No| J{Budget < $20/mo?}
    J -->|Yes| I
    J -->|No| K{Connector breadth\nis the priority?}
    K -->|Yes| G
    K -->|No| I

    style D fill:#f3e5f5,stroke:#6A1B9A
    style G fill:#e3f2fd,stroke:#1565C0
    style I fill:#e8f5e9,stroke:#2E7D32
    style F fill:#e8f5e9,stroke:#2E7D32
```
