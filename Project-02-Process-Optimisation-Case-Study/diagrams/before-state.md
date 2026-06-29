# Before-State: Manual Case Handling Process

```mermaid
flowchart TD
    A([Engineering team\nencounters a problem]) -->|Composes free-form\nemail| B[Shared team inbox]

    B --> C{First available\nengineer checks inbox}

    C -->|Reads email,\nmakes urgency judgement| D[Self-assigns\nby replying-all]

    D --> E{Was someone\nelse already\nworking on it?}

    E -->|Yes — duplicate\nhandling| F[/Coordination\noverhead\nwasted effort/]
    E -->|No| G[Begins working\non the case]

    G --> H[Updates shared\nspreadsheet manually]

    H --> I{Case resolved\nwithin SLA?}

    I -->|Yes| J([Case closed\nSpreadsheet updated])

    I -->|No — escalation\ndiscovered by chance| K{Someone notices\nstale email in inbox}

    K -->|Often too late| L[/SLA breach\nno proactive alert/]
    K -->|Picks it up manually| G

    subgraph PAIN ["Pain points"]
        F
        L
        M[/No urgency signal\nat intake/]
        N[/No structured data\nreporting impossible/]
        O[/Spreadsheet stale\nwithin hours/]
    end

    B -.->|All case types\narrived identically| M
    H -.->|Updated inconsistently| O
    J -.->|No category data\ncaptured| N

    style PAIN fill:#ffebee,stroke:#e53935
    style A fill:#e3f2fd,stroke:#1976D2
    style J fill:#e8f5e9,stroke:#388E3C
    style F fill:#ffcdd2,stroke:#e53935
    style L fill:#ffcdd2,stroke:#e53935
    style M fill:#ffcdd2,stroke:#e53935
    style N fill:#ffcdd2,stroke:#e53935
    style O fill:#ffcdd2,stroke:#e53935
```

---

## Step-by-step breakdown

| Step | Actor | Action | Time cost | Problem |
|---|---|---|---|---|
| 1 | Engineering team | Writes free-form email to shared alias | — | No structure; urgency invisible |
| 2 | All engineers | Monitor shared inbox | Passive background attention | Distracting; no signal-to-noise filtering |
| 3 | First available | Reads email, judges urgency informally | ~5 min per case | Inconsistent — same case rated differently by different engineers |
| 4 | First available | Replies-all to claim the case | ~2 min | Race condition — two engineers often start simultaneously |
| 5 | Assignee | Works the case | Varies | No context pre-loaded; must re-read full email chain |
| 6 | Assignee | Updates spreadsheet | ~3 min | Manual; frequently skipped under pressure |
| 7 | Anyone | Notices old unresolved email | Reactive | SLA breach discovered after the fact, not before |
| 8 | Assignee or team lead | Escalates informally | ~5 min | No consistent escalation path |

**Total overhead per case (triage + tracking): ~15–20 min**
**Team overhead per week (~110 cases): ~27–37 engineer-hours**
