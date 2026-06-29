"""
Onboarding pipeline orchestrator.

Runs each step in sequence, records timing and status for every step, and
returns a full pipeline trace regardless of individual step outcomes.

Critical steps (crm_create, email_generate, email_send) halt the pipeline
on failure. Non-critical steps (slack_notify, crm_update) log the error and
continue so a partial failure never silently swallows the core delivery.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable


@dataclass
class StepResult:
    step: str
    status: str          # "success" | "failed" | "skipped"
    at: str              # ISO 8601 UTC
    duration_ms: int
    detail: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class PipelineTrace:
    run_id: str
    client_id: str
    started_at: str
    completed_at: str = ""
    total_duration_ms: int = 0
    outcome: str = "success"    # "success" | "partial" | "failed"
    steps: list[StepResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "client_id": self.client_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_duration_ms": self.total_duration_ms,
            "outcome": self.outcome,
            "steps": [
                {
                    "step": s.step,
                    "status": s.status,
                    "at": s.at,
                    "duration_ms": s.duration_ms,
                    "detail": s.detail,
                    **s.data,
                }
                for s in self.steps
            ],
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_step(
    name: str,
    fn: Callable[[], dict],
    critical: bool,
    trace: PipelineTrace,
) -> tuple[bool, dict]:
    """
    Execute a pipeline step, capture timing, append to trace.
    Returns (continue_pipeline, result_data).
    """
    started = time.monotonic()
    at = _now_iso()
    try:
        result_data = fn()
        duration_ms = int((time.monotonic() - started) * 1000)
        trace.steps.append(
            StepResult(
                step=name,
                status="success",
                at=at,
                duration_ms=duration_ms,
                data=result_data or {},
            )
        )
        return True, result_data or {}
    except Exception as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        trace.steps.append(
            StepResult(
                step=name,
                status="failed",
                at=at,
                duration_ms=duration_ms,
                detail=str(exc),
            )
        )
        if critical:
            trace.outcome = "failed"
            return False, {}
        else:
            if trace.outcome == "success":
                trace.outcome = "partial"
            return True, {}


@dataclass
class OnboardingPayload:
    first_name: str
    last_name: str
    email: str
    company_name: str
    industry: str
    company_size: str    # "1-10" | "11-50" | "51-200" | "200+"
    plan: str            # "starter" | "professional" | "enterprise"
    account_manager: str
    use_case: str
    source: str


def run_onboarding_pipeline(
    payload: OnboardingPayload,
    crm,
    email_generator,
    email_sender,
    slack_notifier,
) -> PipelineTrace:
    """
    Execute the five-step onboarding pipeline and return a full trace.

    Steps
    -----
    1. crm_create       (critical) — create client record in Airtable
    2. email_generate   (critical) — generate personalised welcome email via Claude
    3. email_send       (critical) — deliver email via SendGrid
    4. slack_notify     (non-critical) — alert account manager in Slack
    5. crm_update       (non-critical) — write delivery timestamps back to CRM record
    """
    client_id = f"CLT-{uuid.uuid4().hex[:6].upper()}"
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    pipeline_start = time.monotonic()

    trace = PipelineTrace(
        run_id=run_id,
        client_id=client_id,
        started_at=_now_iso(),
    )

    # --- Step 1: CRM record creation ---
    crm_record_id: str = ""

    def step_crm_create() -> dict:
        nonlocal crm_record_id
        row = crm.create_client(client_id=client_id, payload=payload)
        crm_record_id = row.get("id", "")
        return {"crm_record_id": crm_record_id}

    ok, _ = _run_step("crm_create", step_crm_create, critical=True, trace=trace)
    if not ok:
        _finalise(trace, pipeline_start)
        return trace

    # --- Step 2: Email generation ---
    generated_subject: str = ""
    generated_body: str = ""

    def step_email_generate() -> dict:
        nonlocal generated_subject, generated_body
        result = email_generator.generate(payload=payload)
        generated_subject = result["subject"]
        generated_body = result["body"]
        return {"subject": generated_subject}

    ok, _ = _run_step("email_generate", step_email_generate, critical=True, trace=trace)
    if not ok:
        _finalise(trace, pipeline_start)
        return trace

    # --- Step 3: Email delivery ---
    def step_email_send() -> dict:
        message_id = email_sender.send(
            to_email=payload.email,
            to_name=f"{payload.first_name} {payload.last_name}",
            subject=generated_subject,
            body_html=generated_body,
        )
        return {"message_id": message_id}

    ok, _ = _run_step("email_send", step_email_send, critical=True, trace=trace)
    if not ok:
        _finalise(trace, pipeline_start)
        return trace

    # --- Step 4: Slack notification (non-critical) ---
    def step_slack_notify() -> dict:
        slack_notifier.notify_account_manager(
            client_id=client_id,
            payload=payload,
            crm_record_id=crm_record_id,
        )
        return {}

    _run_step("slack_notify", step_slack_notify, critical=False, trace=trace)

    # --- Step 5: CRM update with delivery timestamps (non-critical) ---
    def step_crm_update() -> dict:
        crm.update_onboarding_status(
            record_id=crm_record_id,
            welcome_email_sent=True,
            am_notified=trace.steps[-1].status == "success",
        )
        return {}

    _run_step("crm_update", step_crm_update, critical=False, trace=trace)

    _finalise(trace, pipeline_start)
    return trace


def _finalise(trace: PipelineTrace, start: float) -> None:
    trace.completed_at = _now_iso()
    trace.total_duration_ms = int((time.monotonic() - start) * 1000)
