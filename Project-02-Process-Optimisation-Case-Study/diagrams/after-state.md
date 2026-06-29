# After-State: Automated Case Routing & Escalation Workflow

```mermaid
flowchart TD
    A([Engineering team\nencounters a problem]) -->|Submits structured\nintake form| B

    subgraph INTAKE ["Intake Layer"]
        B[Intake Form\ntool · issue type · urgency · description]
    end

    subgraph ENGINE ["Classification Engine (Rules-based)"]
        C[Parse structured fields]
        D{Issue type\n+ urgency signal}
        C --> D
        D -->|Production blocked| E1[P1 Critical — SLA 15 min]
        D -->|Service degraded| E2[P2 High — SLA 1 h]
        D -->|Functional question| E3[P3 Medium — SLA 4 h]
        D -->|General / docs| E4[P4 Low — SLA 8 h]
    end

    subgraph ASSIGN ["Assignment Engine"]
        F[Round-robin within\ntier-appropriate subgroup]
        G[Case record written\nto central data store]
        H[Assignee notified\nwith full context pre-loaded]
        F --> G --> H
    end

    subgraph SLA ["SLA Watcher (runs every 15 min)"]
        I{Check all open cases\nagainst SLA deadline}
        I -->|≥ 80% elapsed,\nno response| J[Nudge to assignee]
        I -->|100% elapsed,\nno response| K[Escalation to team lead\n+ case context attached]
        I -->|Within SLA| L[No action]
    end

    subgraph RESOLVE ["Resolution"]
        M[Case closed\nresolution recorded]
        N[Metrics written\nto dashboard]
    end

    B --> C
    E1 & E2 & E3 & E4 --> F
    G --> SLA
    H --> |Assignee works case| M
    M --> N

    style INTAKE fill:#e3f2fd,stroke:#1976D2
    style ENGINE fill:#f3e5f5,stroke:#7B1FA2
    style ASSIGN fill:#fff8e1,stroke:#F57F17
    style SLA fill:#fce4ec,stroke:#C62828
    style RESOLVE fill:#e8f5e9,stroke:#2E7D32
```

---

## Step-by-step breakdown

| Step | Actor | Action | Time cost | Improvement over before |
|---|---|---|---|---|
| 1 | Engineering team | Fills structured intake form | ~2 min | Form enforces required fields; urgency is explicit |
| 2 | Automation | Classifies case into P1–P4 tier | < 1 s | Deterministic; no engineer judgement needed |
| 3 | Automation | Assigns to engineer via round-robin | < 1 s | Race condition eliminated; no reply-all noise |
| 4 | Automation | Writes case record to data store | < 1 s | Data accurate and queryable in real time |
| 5 | Automation | Notifies assignee with full context | < 1 s | Engineer receives a structured brief, not a raw email |
| 6 | Assignee | Works the case | Varies | No inbox scanning; no spreadsheet update required |
| 7 | SLA Watcher | Checks open cases every 15 min | Automated | Proactive nudge before breach; escalation at breach |
| 8 | Assignee | Closes case — automation records resolution | < 1 s | Metrics captured automatically; no manual update |

**Total human overhead per case (triage + tracking): ~2 min**
**Team overhead per week (~110 cases): ~3–4 engineer-hours (vs. 27–37 before)**

---

## Key Differences at a Glance

| Dimension | Before | After |
|---|---|---|
| Intake | Free-form email | Structured form with required fields |
| Classification | Manual, informal, inconsistent | Rules-based, deterministic, auditable |
| Assignment | Self-assign race condition | Round-robin, collision-free |
| SLA visibility | None | Real-time dashboard + proactive alerts |
| Escalation | Reactive, by memory | Automatic at 80% and 100% of SLA |
| Data quality | ~60% spreadsheet accuracy | ~99% automated record accuracy |
| Engineer triage overhead | ~4.5 h/week | ~0.4 h/week |
