"""
Azure Function — Compliance Report AI Summary Endpoint

Called by the Power Automate flow via HTTP action.
Receives the structured compliance payload, sends it to Claude,
and returns a structured JSON summary for the flow to embed
in the HTML report and Teams card.

Deploy to Azure Functions (Python v2 model).
Runtime: Python 3.11+
Auth level: Function (key required via x-functions-key header)
"""

from __future__ import annotations

import json
import logging
import os

import anthropic
import azure.functions as func

app = func.FunctionApp()
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior compliance analyst writing for a leadership audience.
Your job is to summarise a weekly compliance check report clearly, concisely, and without jargon.

Always respond with a single valid JSON object — no markdown fencing, no prose outside the JSON.
""".strip()

USER_PROMPT_TEMPLATE = """
You have received the following weekly compliance data for the report period: {report_period}

SUMMARY STATS:
- Total compliance checks reviewed: {total_checks}
- Checks requiring attention: {items_with_issues}
- Compliant: {compliant_count}

ITEMS REQUIRING ATTENTION:
{items_text}

Write a compliance report summary as a JSON object with exactly these keys:

- executive_summary     : 2-3 sentence paragraph for the leadership audience; lead with the most
                          important risk signal; do not use bullet points here
- risk_assessment       : 1-2 sentences on the overall risk level this week (Low / Medium / High / Critical)
                          and what is driving it
- key_findings          : list of 3-5 HTML <li> strings (each a specific, concrete finding — not generic)
- recommended_actions   : list of 3-4 HTML <li> strings (specific, owner-assigned actions where possible)
- trend_note            : 1 sentence comparing this week to a typical week, or noting if data is
                          insufficient for a trend (do not fabricate trend data)

Respond with JSON only.
""".strip()


def _format_items_text(items: list[dict]) -> str:
    if not items:
        return "No items requiring attention this period."
    lines = []
    for item in items[:30]:  # cap at 30 to manage token count
        missing = item.get("MissingFields", "")
        missing_note = f" [Missing: {missing.rstrip(';')}]" if missing else ""
        lines.append(
            f"- [{item.get('RiskLevel', 'Unknown')} risk] {item.get('ComplianceArea', 'N/A')} — "
            f"{item.get('CheckName', 'N/A')} | Status: {item.get('Status', 'N/A')} | "
            f"Owner: {item.get('Owner', 'Unassigned')} | "
            f"Findings: {item.get('FindingCount', 0)}{missing_note}"
        )
    if len(items) > 30:
        lines.append(f"... and {len(items) - 30} additional items (truncated for summary)")
    return "\n".join(lines)


@app.function_name(name="GenerateComplianceSummary")
@app.route(route="generate-summary", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def generate_compliance_summary(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("GenerateComplianceSummary triggered")

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body"}),
            status_code=400,
            mimetype="application/json",
        )

    required_keys = ("report_title", "report_period", "total_checks", "items_with_issues")
    missing = [k for k in required_keys if k not in payload]
    if missing:
        return func.HttpResponse(
            json.dumps({"error": "missing_fields", "fields": missing}),
            status_code=400,
            mimetype="application/json",
        )

    items = payload.get("items", [])
    items_text = _format_items_text(items)

    user_message = USER_PROMPT_TEMPLATE.format(
        report_period=payload["report_period"],
        total_checks=payload["total_checks"],
        items_with_issues=payload["items_with_issues"],
        compliant_count=payload.get("compliant_count", "N/A"),
        items_text=items_text,
    )

    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text.strip()
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.exception("Claude returned non-JSON response")
        return func.HttpResponse(
            json.dumps({"error": "AI response parse error", "detail": str(exc)}),
            status_code=502,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.exception("Claude API call failed")
        return func.HttpResponse(
            json.dumps({"error": "AI generation failed", "detail": str(exc)}),
            status_code=502,
            mimetype="application/json",
        )

    logger.info(
        "Summary generated for '%s': %d items reviewed",
        payload.get("report_title"),
        payload.get("total_checks", 0),
    )

    return func.HttpResponse(
        json.dumps(result),
        status_code=200,
        mimetype="application/json",
    )
