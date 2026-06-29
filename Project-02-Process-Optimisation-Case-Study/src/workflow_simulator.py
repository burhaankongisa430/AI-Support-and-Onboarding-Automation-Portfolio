"""
Workflow Simulator — Case Routing & SLA Tracking

This script is a standalone, runnable demonstration of the three core automation
components described in the case study:

    1. ClassificationEngine  — rules-based tier and SLA assignment
    2. AssignmentEngine      — round-robin engineer assignment
    3. SLAWatcher            — proactive nudge and escalation logic

Run it with no arguments to process the bundled sample cases and print a full
simulation report:

    python src/workflow_simulator.py

This is not the production system — it is a distilled code representation of
the architectural patterns used, written to make the case study concrete.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------

class Tier(str, Enum):
    P1 = "P1 Critical"
    P2 = "P2 High"
    P3 = "P3 Medium"
    P4 = "P4 Low"


SLA_MINUTES: dict[Tier, int] = {
    Tier.P1: 15,
    Tier.P2: 60,
    Tier.P3: 240,
    Tier.P4: 480,
}

URGENCY_PROMOTES: dict[str, int] = {
    "critical": -1,  # promotes one tier up (lower index = higher priority)
    "high": 0,
    "medium": 0,
    "low": +1,       # demotes one tier down
}

TIER_ORDER = [Tier.P1, Tier.P2, Tier.P3, Tier.P4]


@dataclass
class Case:
    case_id: str
    requester_email: str
    team: str
    tool_name: str
    issue_type: str
    urgency_self_assessed: str
    description: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tier: Tier | None = None
    sla_deadline: datetime | None = None
    assignee: str | None = None
    status: str = "Open"
    first_response_at: datetime | None = None
    resolved_at: datetime | None = None
    nudge_sent: bool = False
    escalation_sent: bool = False

    def elapsed_pct(self, now: datetime) -> float:
        if self.sla_deadline is None:
            return 0.0
        total = (self.sla_deadline - self.created_at).total_seconds()
        elapsed = (now - self.created_at).total_seconds()
        return elapsed / total if total > 0 else 0.0

    def is_breached(self, now: datetime) -> bool:
        return self.sla_deadline is not None and now >= self.sla_deadline

    def time_to_assignment(self) -> str:
        """Returns a human-readable string — immediate for automated assignment."""
        return "< 1 second (automated)"


# ---------------------------------------------------------------------------
# Classification Engine
# ---------------------------------------------------------------------------

ISSUE_TYPE_TO_BASE_TIER: dict[str, Tier] = {
    "production_blocked": Tier.P1,
    "service_degraded": Tier.P2,
    "critical_defect": Tier.P2,
    "defect": Tier.P3,
    "integration_issue": Tier.P3,
    "functional_question": Tier.P3,
    "general_question": Tier.P4,
    "documentation": Tier.P4,
    "feature_request": Tier.P4,
}


class ClassificationEngine:
    def classify(self, issue_type: str, urgency_self_assessed: str) -> tuple[Tier, bool]:
        """
        Returns (tier, promoted) where promoted=True means the urgency signal
        overrode the issue-type base tier. A promoted case is flagged for human review.
        """
        base_tier = ISSUE_TYPE_TO_BASE_TIER.get(issue_type, Tier.P4)
        base_idx = TIER_ORDER.index(base_tier)

        urgency_key = urgency_self_assessed.lower()
        shift = URGENCY_PROMOTES.get(urgency_key, 0)
        adjusted_idx = max(0, min(len(TIER_ORDER) - 1, base_idx + shift))

        final_tier = TIER_ORDER[adjusted_idx]
        promoted = adjusted_idx != base_idx

        return final_tier, promoted

    def assign_sla(self, tier: Tier, created_at: datetime) -> datetime:
        return created_at + timedelta(minutes=SLA_MINUTES[tier])


# ---------------------------------------------------------------------------
# Assignment Engine
# ---------------------------------------------------------------------------

class AssignmentEngine:
    def __init__(self, engineers_by_tier: dict[Tier, list[str]]):
        self._queues: dict[Tier, list[str]] = {
            tier: list(engineers) for tier, engineers in engineers_by_tier.items()
        }
        self._pointers: dict[Tier, int] = {tier: 0 for tier in Tier}

    def assign(self, tier: Tier) -> str:
        queue = self._queues.get(tier, self._queues[Tier.P4])
        if not queue:
            return "unassigned"
        idx = self._pointers[tier] % len(queue)
        assignee = queue[idx]
        self._pointers[tier] += 1
        return assignee


# ---------------------------------------------------------------------------
# SLA Watcher
# ---------------------------------------------------------------------------

class SLAWatcher:
    def __init__(
        self,
        nudge_fn: Callable[[Case], None],
        escalate_fn: Callable[[Case], None],
    ):
        self._nudge = nudge_fn
        self._escalate = escalate_fn

    def check(self, cases: list[Case], now: datetime) -> dict[str, int]:
        stats = {"checked": 0, "nudges": 0, "escalations": 0}
        for case in cases:
            if case.status == "Resolved":
                continue
            stats["checked"] += 1
            pct = case.elapsed_pct(now)
            if pct >= 1.0 and not case.escalation_sent:
                self._escalate(case)
                case.escalation_sent = True
                case.status = "Escalated"
                stats["escalations"] += 1
            elif pct >= 0.8 and not case.nudge_sent:
                self._nudge(case)
                case.nudge_sent = True
                stats["nudges"] += 1
        return stats


# ---------------------------------------------------------------------------
# Notification stubs (print-based for simulation)
# ---------------------------------------------------------------------------

def send_assignee_notification(case: Case) -> None:
    print(
        f"  [NOTIFY] {case.assignee} assigned {case.case_id} "
        f"({case.tier.value}) — SLA deadline "
        f"{case.sla_deadline.strftime('%H:%M UTC') if case.sla_deadline else 'N/A'}"
    )


def send_nudge(case: Case) -> None:
    print(
        f"  [NUDGE ] {case.assignee} — {case.case_id} is approaching SLA "
        f"({case.tier.value})"
    )


def send_escalation(case: Case) -> None:
    print(
        f"  [ESCAL ] Team lead — {case.case_id} has BREACHED SLA "
        f"({case.tier.value}) — assignee: {case.assignee}"
    )


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

SAMPLE_SUBMISSIONS = [
    {
        "requester_email": "alex.patel@internal.example",
        "team": "Platform Engineering",
        "tool_name": "deploy-accelerator",
        "issue_type": "production_blocked",
        "urgency_self_assessed": "Critical",
        "description": "Deployment pipeline is completely down. All production releases blocked.",
    },
    {
        "requester_email": "maria.osei@internal.example",
        "team": "Data Infrastructure",
        "tool_name": "etl-runner",
        "issue_type": "service_degraded",
        "urgency_self_assessed": "High",
        "description": "ETL jobs completing 10x slower than normal since this morning.",
    },
    {
        "requester_email": "james.white@internal.example",
        "team": "Security",
        "tool_name": "audit-logger",
        "issue_type": "defect",
        "urgency_self_assessed": "Medium",
        "description": "Audit logs not capturing DELETE operations correctly.",
    },
    {
        "requester_email": "sara.kim@internal.example",
        "team": "Developer Experience",
        "tool_name": "cli-toolkit",
        "issue_type": "functional_question",
        "urgency_self_assessed": "Low",
        "description": "Unsure how to configure the --region flag for multi-region deployments.",
    },
    {
        "requester_email": "chris.ngozi@internal.example",
        "team": "Cost Optimisation",
        "tool_name": "cost-reporter",
        "issue_type": "feature_request",
        "urgency_self_assessed": "Low",
        "description": "Would be great to have a weekly email digest of the cost report.",
    },
    {
        "requester_email": "priya.gupta@internal.example",
        "team": "Reliability",
        "tool_name": "canary-runner",
        "issue_type": "integration_issue",
        "urgency_self_assessed": "Critical",  # self-assessed higher than issue type
        "description": "Canary tests failing to integrate with the new metrics endpoint.",
    },
]

ENGINEERS = {
    Tier.P1: ["alice", "bob"],
    Tier.P2: ["alice", "bob", "carol"],
    Tier.P3: ["carol", "dan", "eve"],
    Tier.P4: ["dan", "eve"],
}


def run_simulation() -> None:
    print("=" * 65)
    print("  CASE ROUTING & SLA TRACKING — WORKFLOW SIMULATOR")
    print("=" * 65)

    classifier = ClassificationEngine()
    assigner = AssignmentEngine(ENGINEERS)
    watcher = SLAWatcher(nudge_fn=send_nudge, escalate_fn=send_escalation)

    base_time = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    cases: list[Case] = []

    print("\n--- INTAKE & ROUTING ---\n")

    for i, submission in enumerate(SAMPLE_SUBMISSIONS):
        # Stagger case arrivals for simulation realism
        created_at = base_time + timedelta(minutes=i * 3)

        tier, promoted = classifier.classify(
            submission["issue_type"],
            submission["urgency_self_assessed"],
        )
        sla_deadline = classifier.assign_sla(tier, created_at)
        assignee = assigner.assign(tier)

        case = Case(
            case_id=f"CASE-{uuid.uuid4().hex[:6].upper()}",
            created_at=created_at,
            tier=tier,
            sla_deadline=sla_deadline,
            assignee=assignee,
            **{k: v for k, v in submission.items()},
        )
        cases.append(case)

        promotion_flag = " [PROMOTED — flagged for review]" if promoted else ""
        print(
            f"  {case.case_id}  {tier.value:<16}  assignee={assignee:<8}"
            f"  SLA={SLA_MINUTES[tier]:>4} min  {submission['tool_name']}"
            f"{promotion_flag}"
        )
        send_assignee_notification(case)

    print("\n--- SLA WATCHER SIMULATION ---\n")
    print("  Simulating watcher runs at T+10min, T+30min, T+60min, T+4h, T+8h:\n")

    check_offsets = [10, 30, 60, 240, 480]
    for offset in check_offsets:
        now = base_time + timedelta(minutes=offset)
        stats = watcher.check(cases, now)
        if stats["nudges"] > 0 or stats["escalations"] > 0:
            print(
                f"  T+{offset:>4}min — checked {stats['checked']} open cases  "
                f"nudges={stats['nudges']}  escalations={stats['escalations']}"
            )

    print("\n--- CASE SUMMARY ---\n")
    header = f"  {'Case ID':<18} {'Tier':<16} {'Assignee':<10} {'Status':<12} {'Tool'}"
    print(header)
    print("  " + "-" * 70)
    for case in cases:
        print(
            f"  {case.case_id:<18} {case.tier.value:<16} {case.assignee:<10}"
            f" {case.status:<12} {case.tool_name}"
        )

    print("\n--- BEFORE vs AFTER METRICS ---\n")
    rows = [
        ("Mean time to first assignment", "3 h 47 min", "< 1 second", "-98%"),
        ("SLA breach rate", "34%", "3%", "-91%"),
        ("Duplicate-handling incidents/week", "~6", "0", "-100%"),
        ("Triage + tracking time / engineer / week", "4.5 h", "0.4 h", "-91%"),
        ("Data accuracy (case records)", "~60%", "~99%", "+65%"),
    ]
    print(f"  {'Metric':<44} {'Before':<14} {'After':<12} {'Change'}")
    print("  " + "-" * 80)
    for metric, before, after, change in rows:
        print(f"  {metric:<44} {before:<14} {after:<12} {change}")

    print("\n" + "=" * 65)
    print("  Simulation complete.")
    print("=" * 65)


if __name__ == "__main__":
    run_simulation()
