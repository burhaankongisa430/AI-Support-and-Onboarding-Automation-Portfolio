"""
AI Automation Platform Scoring Model

A reproducible, data-driven implementation of the evaluation methodology
described in evaluation/02-criteria.md. Running this script regenerates the
full comparison matrix, sensitivity analysis, and cost comparison from the
raw scores defined below.

This makes the evaluation auditable: changing a score or weight produces a
new result immediately, so any reader can verify or challenge the methodology
by modifying the inputs and re-running.

Usage:
    python src/scoring_model.py
    python src/scoring_model.py --format markdown
    python src/scoring_model.py --sensitivity
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Criterion:
    name: str
    weight: float          # 0.0–1.0
    description: str = ""


@dataclass
class PlatformScore:
    platform: str
    scores: dict[str, int]  # criterion name → raw score (1–10)

    def weighted_total(self, criteria: list[Criterion]) -> float:
        return sum(
            self.scores[c.name] * c.weight
            for c in criteria
            if c.name in self.scores
        )

    def weighted_score(self, criterion: Criterion) -> float:
        return self.scores.get(criterion.name, 0) * criterion.weight


@dataclass
class CostProfile:
    platform: str
    plan_name: str
    monthly_cost: float
    ops_included: str
    ops_used_per_month: int
    headroom_multiplier: float
    cost_at_5x_volume: float
    cost_at_20x_volume: float


# ---------------------------------------------------------------------------
# Evaluation data
# ---------------------------------------------------------------------------

CRITERIA: list[Criterion] = [
    Criterion("cost",          0.20, "Monthly cost at SME scale (~150 runs/month)"),
    Criterion("ease",          0.15, "Ease of implementation for a non-developer"),
    Criterion("ai_integration",0.25, "AI integration depth (Claude/OpenAI, dynamic context, parsing)"),
    Criterion("reliability",   0.15, "Reliability and error handling"),
    Criterion("scalability",   0.10, "Scalability in volume and complexity"),
    Criterion("ecosystem",     0.10, "App connector breadth for this scenario's 6 apps"),
    Criterion("governance",    0.05, "Audit trail, version history, access control"),
]

PLATFORM_SCORES: list[PlatformScore] = [
    PlatformScore(
        platform="Zapier",
        scores={
            "cost":           5,
            "ease":           9,
            "ai_integration": 6,
            "reliability":    7,
            "scalability":    6,
            "ecosystem":      10,
            "governance":     5,
        },
    ),
    PlatformScore(
        platform="Make",
        scores={
            "cost":           9,
            "ease":           7,
            "ai_integration": 8,
            "reliability":    8,
            "scalability":    8,
            "ecosystem":      8,
            "governance":     6,
        },
    ),
    PlatformScore(
        platform="Power Automate",
        scores={
            "cost":           6,
            "ease":           4,
            "ai_integration": 7,
            "reliability":    9,
            "scalability":    9,
            "ecosystem":      7,
            "governance":     9,
        },
    ),
]

COST_PROFILES: list[CostProfile] = [
    CostProfile(
        platform="Zapier",
        plan_name="Professional",
        monthly_cost=73.50,
        ops_included="2,000 tasks",
        ops_used_per_month=90,
        headroom_multiplier=22.2,
        cost_at_5x_volume=73.50,
        cost_at_20x_volume=199.00,
    ),
    CostProfile(
        platform="Make",
        plan_name="Core",
        monthly_cost=9.00,
        ops_included="10,000 ops",
        ops_used_per_month=90,
        headroom_multiplier=111.1,
        cost_at_5x_volume=9.00,
        cost_at_20x_volume=16.00,
    ),
    CostProfile(
        platform="Power Automate",
        plan_name="Premium (2 users)",
        monthly_cost=30.00,
        ops_included="Unlimited (connector-gated)",
        ops_used_per_month=90,
        headroom_multiplier=float("inf"),
        cost_at_5x_volume=30.00,
        cost_at_20x_volume=30.00,
    ),
]


# ---------------------------------------------------------------------------
# Scoring engine
# ---------------------------------------------------------------------------

def compute_results(
    criteria: list[Criterion],
    platform_scores: list[PlatformScore],
) -> list[dict]:
    results = []
    for ps in platform_scores:
        row = {"platform": ps.platform}
        for c in criteria:
            row[c.name] = ps.scores.get(c.name, 0)
            row[f"{c.name}_weighted"] = round(ps.weighted_score(c), 3)
        row["total"] = round(ps.weighted_total(criteria), 3)
        results.append(row)
    return sorted(results, key=lambda r: r["total"], reverse=True)


def sensitivity_analysis(
    base_criteria: list[Criterion],
    platform_scores: list[PlatformScore],
    scenarios: list[tuple[str, dict[str, float]]],
) -> list[dict]:
    """
    Run alternative weight scenarios to test recommendation robustness.
    Each scenario is (name, {criterion_name: new_weight}).
    Unspecified criteria keep their base weight, renormalised to sum to 1.0.
    """
    rows = []
    for scenario_name, overrides in scenarios:
        adjusted = []
        for c in base_criteria:
            new_weight = overrides.get(c.name, c.weight)
            adjusted.append(Criterion(c.name, new_weight, c.description))
        total_weight = sum(c.weight for c in adjusted)
        normalised = [Criterion(c.name, c.weight / total_weight, c.description) for c in adjusted]
        results = compute_results(normalised, platform_scores)
        winner = results[0]["platform"]
        scores = {r["platform"]: r["total"] for r in results}
        rows.append({"scenario": scenario_name, "winner": winner, **scores})
    return rows


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _col_widths(headers: list[str], rows: list[list]) -> list[int]:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    return widths


def _print_table(headers: list[str], rows: list[list], fmt: str = "plain") -> None:
    widths = _col_widths(headers, rows)
    if fmt == "markdown":
        sep = " | "
        header_line = sep.join(h.ljust(w) for h, w in zip(headers, widths))
        divider = " | ".join("-" * w for w in widths)
        print(f"| {header_line} |")
        print(f"| {divider} |")
        for row in rows:
            line = sep.join(str(c).ljust(w) for c, w in zip(row, widths))
            print(f"| {line} |")
    else:
        header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
        print(header_line)
        print("  ".join("-" * w for w in widths))
        for row in rows:
            print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))


def print_summary(results: list[dict], criteria: list[Criterion], fmt: str = "plain") -> None:
    print("\n" + "=" * 65)
    print("  WEIGHTED SCORE SUMMARY")
    print("=" * 65)
    headers = ["Platform"] + [c.name.replace("_", " ").title() for c in criteria] + ["Total"]
    rows = []
    for r in results:
        row = [r["platform"]]
        for c in criteria:
            row.append(f"{r[c.name]} ({r[f'{c.name}_weighted']:.2f})")
        row.append(f"**{r['total']}**" if fmt == "markdown" else f"{r['total']}")
        rows.append(row)
    _print_table(headers, rows, fmt)
    print()


def print_raw_scores(results: list[dict], criteria: list[Criterion], fmt: str = "plain") -> None:
    print("\n" + "=" * 65)
    print("  RAW SCORES")
    print("=" * 65)
    headers = ["Criterion", "Weight"] + [r["platform"] for r in results]
    rows = []
    for c in criteria:
        row = [c.name.replace("_", " ").title(), f"{int(c.weight * 100)}%"]
        for r in results:
            row.append(str(r[c.name]))
        rows.append(row)
    _print_table(headers, rows, fmt)
    print()


def print_cost_comparison(profiles: list[CostProfile], fmt: str = "plain") -> None:
    print("\n" + "=" * 65)
    print("  COST COMPARISON")
    print("=" * 65)
    headers = ["Platform", "Plan", "Monthly Cost", "Ops Included", "Headroom", "Cost @5x vol", "Cost @20x vol"]
    rows = []
    for p in profiles:
        hm = f"{p.headroom_multiplier:.0f}×" if p.headroom_multiplier != float("inf") else "N/A"
        rows.append([
            p.platform,
            p.plan_name,
            f"${p.monthly_cost:.2f}",
            p.ops_included,
            hm,
            f"${p.cost_at_5x_volume:.2f}",
            f"${p.cost_at_20x_volume:.2f}",
        ])
    _print_table(headers, rows, fmt)
    print()


def print_sensitivity(sensitivity_rows: list[dict], platform_names: list[str], fmt: str = "plain") -> None:
    print("\n" + "=" * 65)
    print("  SENSITIVITY ANALYSIS")
    print("=" * 65)
    headers = ["Weight Scenario", "Winner"] + platform_names
    rows = []
    for s in sensitivity_rows:
        row = [s["scenario"], s["winner"]]
        for p in platform_names:
            row.append(f"{s.get(p, 0):.2f}")
        rows.append(row)
    _print_table(headers, rows, fmt)
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

SENSITIVITY_SCENARIOS = [
    ("Base weights", {}),
    ("Cost prioritised (+10%)", {"cost": 0.30, "ai_integration": 0.15}),
    ("AI prioritised (+10%)", {"ai_integration": 0.35, "cost": 0.10}),
    ("Ease prioritised (+10%)", {"ease": 0.25, "governance": 0.00}),
    ("Governance prioritised (+10%)", {"governance": 0.15, "ease": 0.05}),
    ("Reliability prioritised (+10%)", {"reliability": 0.25, "scalability": 0.00}),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Platform Scoring Model")
    parser.add_argument("--format", choices=["plain", "markdown"], default="plain")
    parser.add_argument("--sensitivity", action="store_true")
    args = parser.parse_args()

    fmt = args.format
    results = compute_results(CRITERIA, PLATFORM_SCORES)

    print("\n" + "=" * 65)
    print("  AI AUTOMATION PLATFORM EVALUATION")
    print("  Scenario: Client Onboarding — 20-person Remote Professional Services Firm")
    print("=" * 65)

    print_raw_scores(results, CRITERIA, fmt)
    print_summary(results, CRITERIA, fmt)
    print_cost_comparison(COST_PROFILES, fmt)

    if args.sensitivity:
        platform_names = [ps.platform for ps in PLATFORM_SCORES]
        sensitivity_rows = sensitivity_analysis(CRITERIA, PLATFORM_SCORES, SENSITIVITY_SCENARIOS)
        print_sensitivity(sensitivity_rows, platform_names, fmt)

    print("\n" + "=" * 65)
    winner = results[0]
    print(f"  RECOMMENDATION: {winner['platform']}  (score: {winner['total']}/10.00)")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
