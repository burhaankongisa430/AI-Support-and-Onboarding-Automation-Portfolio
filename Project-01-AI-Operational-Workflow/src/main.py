"""
Support Ticket Triage — webhook server entry point.

Accepts POST requests from Zapier, Make, Google Forms, or any HTTP source,
runs the payload through Claude for AI triage, then writes the enriched
record to Airtable.

Endpoints
---------
POST /webhook/ticket   — main intake endpoint
GET  /health           — liveness check
"""

import logging
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request

from airtable_client import AirtableClient, build_record
from triage import TicketTriageEngine

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
triage_engine = TicketTriageEngine()
airtable = AirtableClient()


@app.get("/health")
def health() -> Response:
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.post("/webhook/ticket")
def receive_ticket() -> tuple[Response, int]:
    """
    Accept an incoming ticket payload (JSON or form data) and run triage.

    Expected fields
    ---------------
    email   : customer email address (required)
    subject : ticket subject line (required)
    body    : full ticket text (required)
    source  : originating channel, e.g. "zapier", "form", "email" (optional)
    """
    if request.is_json:
        data = request.get_json(force=True) or {}
    else:
        data = request.form.to_dict()

    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()
    source = data.get("source", "webhook").strip()

    if not email or not subject or not body:
        return jsonify({"error": "email, subject, and body are required"}), 400

    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    logger.info("Received ticket %s from %s via %s", ticket_id, email, source)

    try:
        result = triage_engine.triage(subject=subject, body=body)
        logger.info(
            "Triage complete for %s — urgency=%s category=%s",
            ticket_id,
            result.urgency,
            result.category,
        )
    except Exception as exc:
        logger.exception("Triage failed for ticket %s", ticket_id)
        return jsonify({"error": "AI triage failed", "detail": str(exc)}), 502

    try:
        record = build_record(
            ticket_id=ticket_id,
            customer_email=email,
            subject=subject,
            body=body,
            source=source,
            triage_result=result,
        )
        airtable_row = airtable.create_ticket(record)
        airtable_record_id = airtable_row.get("id")
        logger.info("Airtable record created: %s", airtable_record_id)
    except Exception as exc:
        logger.exception("Airtable write failed for ticket %s", ticket_id)
        return jsonify({"error": "CRM write failed", "detail": str(exc)}), 502

    return (
        jsonify(
            {
                "ticket_id": ticket_id,
                "airtable_record_id": airtable_record_id,
                "urgency": result.urgency,
                "category": result.category,
                "sentiment": result.sentiment,
                "summary": result.summary,
            }
        ),
        201,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
