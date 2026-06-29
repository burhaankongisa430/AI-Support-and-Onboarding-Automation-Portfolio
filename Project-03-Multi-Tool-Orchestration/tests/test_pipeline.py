"""
Tests for the onboarding pipeline orchestrator.

Unit tests mock all four external service clients so no API keys, CRM
access, or Slack credentials are needed to run the suite.

Run with:
    pytest tests/test_pipeline.py -v
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import OnboardingPayload, PipelineTrace, run_onboarding_pipeline


def _make_payload(**overrides) -> OnboardingPayload:
    defaults = dict(
        first_name="Jordan",
        last_name="Adeyemi",
        email="jordan@nexalogistics.example",
        company_name="Nexa Logistics",
        industry="Logistics & Supply Chain",
        company_size="51-200",
        plan="professional",
        account_manager="Sarah Chen",
        use_case="Automate delivery exception handling",
        source="google_form",
    )
    defaults.update(overrides)
    return OnboardingPayload(**defaults)


def _make_services(
    crm_raises=None,
    email_gen_raises=None,
    email_send_raises=None,
    slack_raises=None,
    crm_update_raises=None,
):
    crm = MagicMock()
    if crm_raises:
        crm.create_client.side_effect = crm_raises
    else:
        crm.create_client.return_value = {"id": "recTEST123"}
    if crm_update_raises:
        crm.update_onboarding_status.side_effect = crm_update_raises

    email_gen = MagicMock()
    if email_gen_raises:
        email_gen.generate.side_effect = email_gen_raises
    else:
        email_gen.generate.return_value = {
            "subject": "Welcome to the platform",
            "body": "<p>Hi Jordan,</p>",
        }

    email_sender = MagicMock()
    if email_send_raises:
        email_sender.send.side_effect = email_send_raises
    else:
        email_sender.send.return_value = "msg-id-123"

    slack = MagicMock()
    if slack_raises:
        slack.notify_account_manager.side_effect = slack_raises

    return crm, email_gen, email_sender, slack


class TestPipelineHappyPath(unittest.TestCase):

    def test_returns_pipeline_trace(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertIsInstance(trace, PipelineTrace)

    def test_outcome_is_success_when_all_steps_pass(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "success")

    def test_five_steps_recorded(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        step_names = [s.step for s in trace.steps]
        self.assertEqual(
            step_names,
            ["crm_create", "email_generate", "email_send", "slack_notify", "crm_update"],
        )

    def test_all_steps_succeed(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        for step in trace.steps:
            self.assertEqual(step.status, "success", f"Expected success on step {step.step}")

    def test_client_id_generated(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertTrue(trace.client_id.startswith("CLT-"))

    def test_run_id_generated(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertTrue(trace.run_id.startswith("RUN-"))

    def test_total_duration_recorded(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertGreater(trace.total_duration_ms, 0)

    def test_to_dict_contains_expected_keys(self):
        crm, gen, sender, slack = _make_services()
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        d = trace.to_dict()
        for key in ("run_id", "client_id", "started_at", "completed_at", "total_duration_ms", "outcome", "steps"):
            self.assertIn(key, d)


class TestPipelineCriticalFailures(unittest.TestCase):

    def test_crm_failure_halts_pipeline(self):
        crm, gen, sender, slack = _make_services(crm_raises=Exception("Airtable timeout"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "failed")
        self.assertEqual(len(trace.steps), 1)
        self.assertEqual(trace.steps[0].status, "failed")

    def test_email_gen_failure_halts_pipeline(self):
        crm, gen, sender, slack = _make_services(email_gen_raises=Exception("Claude API error"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "failed")
        step_names = [s.step for s in trace.steps]
        self.assertIn("crm_create", step_names)
        self.assertNotIn("email_send", step_names)

    def test_email_send_failure_halts_pipeline(self):
        crm, gen, sender, slack = _make_services(email_send_raises=Exception("SendGrid 429"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "failed")
        step_names = [s.step for s in trace.steps]
        self.assertNotIn("slack_notify", step_names)


class TestPipelineNonCriticalFailures(unittest.TestCase):

    def test_slack_failure_produces_partial_outcome(self):
        crm, gen, sender, slack = _make_services(slack_raises=Exception("Slack webhook error"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "partial")

    def test_slack_failure_does_not_stop_crm_update(self):
        crm, gen, sender, slack = _make_services(slack_raises=Exception("Slack webhook error"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        step_names = [s.step for s in trace.steps]
        self.assertIn("crm_update", step_names)

    def test_crm_update_failure_produces_partial_outcome(self):
        crm, gen, sender, slack = _make_services(crm_update_raises=Exception("Airtable error"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        self.assertEqual(trace.outcome, "partial")

    def test_failed_step_records_detail(self):
        crm, gen, sender, slack = _make_services(slack_raises=Exception("connection refused"))
        trace = run_onboarding_pipeline(_make_payload(), crm, gen, sender, slack)
        slack_step = next(s for s in trace.steps if s.step == "slack_notify")
        self.assertIn("connection refused", slack_step.detail)


class TestWebhookEndpoint(unittest.TestCase):

    def setUp(self):
        with (
            patch.dict("os.environ", {
                "ANTHROPIC_API_KEY": "test",
                "AIRTABLE_API_KEY": "test",
                "AIRTABLE_BASE_ID": "appTEST",
                "SENDGRID_API_KEY": "test",
                "SLACK_WEBHOOK_URL": "https://hooks.slack.com/test",
            }),
            patch("crm.requests.Session"),
            patch("email_generator.anthropic.Anthropic"),
            patch("email_sender.requests.post"),
            patch("slack_notifier.requests.post"),
        ):
            import main
            main.app.config["TESTING"] = True
            self.client = main.app.test_client()
            self.mock_trace = MagicMock()
            self.mock_trace.outcome = "success"
            self.mock_trace.run_id = "RUN-TEST"
            self.mock_trace.client_id = "CLT-TEST"
            self.mock_trace.total_duration_ms = 100
            self.mock_trace.to_dict.return_value = {"outcome": "success", "client_id": "CLT-TEST"}
            main.run_onboarding_pipeline = MagicMock(return_value=self.mock_trace)

    def _valid_payload(self):
        return {
            "first_name": "Jordan", "last_name": "Adeyemi",
            "email": "jordan@example.com", "company_name": "Nexa",
            "industry": "Logistics", "company_size": "51-200",
            "plan": "professional", "account_manager": "Sarah Chen",
            "use_case": "Exception handling",
        }

    def test_health_returns_200(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

    def test_valid_payload_returns_201(self):
        resp = self.client.post("/webhook/onboard", json=self._valid_payload())
        self.assertEqual(resp.status_code, 201)

    def test_missing_field_returns_400(self):
        payload = self._valid_payload()
        del payload["email"]
        resp = self.client.post("/webhook/onboard", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_plan_returns_400(self):
        payload = {**self._valid_payload(), "plan": "ultra-mega"}
        resp = self.client.post("/webhook/onboard", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_invalid_company_size_returns_400(self):
        payload = {**self._valid_payload(), "company_size": "huge"}
        resp = self.client.post("/webhook/onboard", json=payload)
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
