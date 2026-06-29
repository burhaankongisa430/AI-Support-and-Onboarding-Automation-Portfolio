"""
Tests for the ticket triage engine.

Unit tests use a mocked Anthropic client so no API key is needed.
Integration tests (marked with pytest.mark.integration) call the real API
and require ANTHROPIC_API_KEY in the environment.

Run unit tests only:
    pytest tests/test_triage.py -v

Run all tests including integration:
    pytest tests/test_triage.py -v -m "integration" --run-integration
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triage import TicketTriageEngine, TriageResult

SAMPLE_TRIAGE_RESPONSE = json.dumps({
    "urgency": "High",
    "category": "Technical",
    "sentiment": "Frustrated",
    "key_issues": [
        "Account locked out since yesterday",
        "Password reset email not arriving",
        "Time-sensitive: client meeting imminent",
    ],
    "summary": "Customer locked out of account with a failing password reset ahead of a client meeting.",
    "suggested_response": (
        "Thank you for contacting us. I completely understand the urgency here and I am "
        "sorry for the disruption this is causing ahead of your meeting. I have escalated "
        "your account to our technical team for immediate attention. In the meantime, please "
        "check your spam folder for the password reset email. If you still cannot access your "
        "account within the next 15 minutes, reply to this message and I will arrange a manual "
        "account reset for you directly. We will get you back in as quickly as possible."
    ),
})


def _make_mock_message(text: str):
    content_block = MagicMock()
    content_block.text = text
    message = MagicMock()
    message.content = [content_block]
    return message


class TestTicketTriageEngineUnit(unittest.TestCase):

    def _engine_with_mock(self, response_text: str) -> TicketTriageEngine:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            engine = TicketTriageEngine()
        engine.client = MagicMock()
        engine.client.messages.create.return_value = _make_mock_message(response_text)
        return engine

    def test_returns_triage_result_dataclass(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        result = engine.triage(subject="Locked out", body="I can't log in.")
        self.assertIsInstance(result, TriageResult)

    def test_urgency_parsed_correctly(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        result = engine.triage(subject="Locked out", body="I can't log in.")
        self.assertEqual(result.urgency, "High")

    def test_category_parsed_correctly(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        result = engine.triage(subject="Locked out", body="I can't log in.")
        self.assertEqual(result.category, "Technical")

    def test_key_issues_is_list(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        result = engine.triage(subject="Locked out", body="I can't log in.")
        self.assertIsInstance(result.key_issues, list)
        self.assertGreater(len(result.key_issues), 0)

    def test_invalid_urgency_falls_back_to_medium(self):
        bad_response = json.dumps({
            "urgency": "SUPER URGENT",
            "category": "Technical",
            "sentiment": "Neutral",
            "key_issues": ["something"],
            "summary": "A summary.",
            "suggested_response": "A response.",
        })
        engine = self._engine_with_mock(bad_response)
        result = engine.triage(subject="x", body="y")
        self.assertEqual(result.urgency, "Medium")

    def test_invalid_category_falls_back_to_general(self):
        bad_response = json.dumps({
            "urgency": "Low",
            "category": "Unknown Category",
            "sentiment": "Neutral",
            "key_issues": ["something"],
            "summary": "A summary.",
            "suggested_response": "A response.",
        })
        engine = self._engine_with_mock(bad_response)
        result = engine.triage(subject="x", body="y")
        self.assertEqual(result.category, "General")

    def test_to_dict_contains_all_keys(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        result = engine.triage(subject="Locked out", body="I can't log in.")
        d = result.to_dict()
        expected_keys = {"urgency", "category", "sentiment", "key_issues", "summary", "suggested_response"}
        self.assertEqual(set(d.keys()), expected_keys)

    def test_prompt_contains_subject_and_body(self):
        engine = self._engine_with_mock(SAMPLE_TRIAGE_RESPONSE)
        engine.triage(subject="My subject", body="My body text")
        call_args = engine.client.messages.create.call_args
        user_content = call_args.kwargs["messages"][0]["content"]
        self.assertIn("My subject", user_content)
        self.assertIn("My body text", user_content)


class TestWebhookEndpointUnit(unittest.TestCase):
    """Tests for the Flask webhook endpoint using a test client."""

    def setUp(self):
        with (
            patch.dict("os.environ", {
                "ANTHROPIC_API_KEY": "test-key",
                "AIRTABLE_API_KEY": "test-key",
                "AIRTABLE_BASE_ID": "appTEST",
            }),
            patch("triage.anthropic.Anthropic"),
            patch("airtable_client.requests.Session"),
        ):
            import main
            main.app.config["TESTING"] = True
            self.client = main.app.test_client()
            self.engine_mock = MagicMock()
            self.airtable_mock = MagicMock()
            main.triage_engine = self.engine_mock
            main.airtable = self.airtable_mock

    def _mock_triage_result(self):
        result = MagicMock()
        result.urgency = "High"
        result.category = "Technical"
        result.sentiment = "Frustrated"
        result.key_issues = ["Issue 1", "Issue 2"]
        result.summary = "A summary."
        result.suggested_response = "A response draft."
        return result

    def test_health_endpoint_returns_200(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ok")

    def test_missing_fields_returns_400(self):
        resp = self.client.post(
            "/webhook/ticket",
            json={"email": "test@example.com"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_valid_payload_returns_201(self):
        self.engine_mock.triage.return_value = self._mock_triage_result()
        self.airtable_mock.create_ticket.return_value = {"id": "recABC123"}

        resp = self.client.post(
            "/webhook/ticket",
            json={
                "email": "user@example.com",
                "subject": "Login broken",
                "body": "I cannot log in at all.",
            },
        )
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertIn("ticket_id", data)
        self.assertEqual(data["urgency"], "High")

    def test_triage_failure_returns_502(self):
        self.engine_mock.triage.side_effect = Exception("API timeout")

        resp = self.client.post(
            "/webhook/ticket",
            json={
                "email": "user@example.com",
                "subject": "Login broken",
                "body": "I cannot log in at all.",
            },
        )
        self.assertEqual(resp.status_code, 502)


if __name__ == "__main__":
    unittest.main()
