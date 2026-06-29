"""
Client Onboarding Pipeline — webhook server entry point.

Accepts a POST from Zapier, Make, or any HTTP source (e.g. a Google Form
webhook) and runs the full five-step onboarding pipeline:

    1. CRM record creation  (Airtable)
    2. Welcome email generation  (Claude)
    3. Welcome email delivery  (SendGrid)
    4. Account manager notification  (Slack)
    5. CRM status update  (Airtable)

Endpoints
---------
POST /webhook/onboard   — trigger the onboarding pipeline
GET  /health            — liveness check
"""

import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request

from crm import AirtableCRMClient
from email_generator import WelcomeEmailGenerator
from email_sender import SendGridEmailSender
from pipeline import OnboardingPayload, run_onboarding_pipeline
from slack_notifier import SlackNotifier

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

crm = AirtableCRMClient()
email_generator = WelcomeEmailGenerator()
email_sender = SendGridEmailSender()
slack_notifier = SlackNotifier()

REQUIRED_FIELDS = (
    "first_name", "last_name", "email", "company_name",
    "industry", "company_size", "plan", "account_manager", "use_case",
)

VALID_PLANS = {"starter", "professional", "enterprise"}
VALID_COMPANY_SIZES = {"1-10", "11-50", "51-200", "200+"}


@app.get("/health")
def health() -> Response:
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})


@app.post("/webhook/onboard")
def onboard_client() -> tuple[Response, int]:
    """
    Trigger the client onboarding pipeline.

    Expected JSON fields
    --------------------
    first_name      : string (required)
    last_name       : string (required)
    email           : string (required)
    company_name    : string (required)
    industry        : string (required)
    company_size    : "1-10" | "11-50" | "51-200" | "200+" (required)
    plan            : "starter" | "professional" | "enterprise" (required)
    account_manager : string (required)
    use_case        : string (required)
    source          : string (optional, default "webhook")
    """
    data = request.get_json(force=True) or {}

    missing = [f for f in REQUIRED_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        return jsonify({"error": "missing_fields", "fields": missing}), 400

    plan = data.get("plan", "").lower().strip()
    if plan not in VALID_PLANS:
        return (
            jsonify({"error": "invalid_plan", "valid_values": list(VALID_PLANS)}),
            400,
        )

    company_size = data.get("company_size", "").strip()
    if company_size not in VALID_COMPANY_SIZES:
        return (
            jsonify({"error": "invalid_company_size", "valid_values": list(VALID_COMPANY_SIZES)}),
            400,
        )

    payload = OnboardingPayload(
        first_name=data["first_name"].strip(),
        last_name=data["last_name"].strip(),
        email=data["email"].strip().lower(),
        company_name=data["company_name"].strip(),
        industry=data["industry"].strip(),
        company_size=company_size,
        plan=plan,
        account_manager=data["account_manager"].strip(),
        use_case=data["use_case"].strip(),
        source=data.get("source", "webhook").strip(),
    )

    logger.info(
        "Onboarding pipeline started for %s (%s) — plan=%s am=%s",
        payload.email,
        payload.company_name,
        payload.plan,
        payload.account_manager,
    )

    trace = run_onboarding_pipeline(
        payload=payload,
        crm=crm,
        email_generator=email_generator,
        email_sender=email_sender,
        slack_notifier=slack_notifier,
    )

    logger.info(
        "Pipeline %s completed in %d ms — outcome=%s client_id=%s",
        trace.run_id,
        trace.total_duration_ms,
        trace.outcome,
        trace.client_id,
    )

    status_code = 201 if trace.outcome == "success" else (207 if trace.outcome == "partial" else 502)
    return jsonify(trace.to_dict()), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
