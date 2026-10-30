from unittest.mock import MagicMock

import anthropic
import httpx2

from narrator import Narrative, generate_narrative

TASKS = [
    {"description": "Invoice entry", "annual_hours": 104, "cost_saved": 3640},
    {"description": "Weekly report", "annual_hours": 52, "cost_saved": 1820},
    {"description": "Inbox triage", "annual_hours": 260, "cost_saved": 9100},
]
TOTALS = {"annual_hours": 416, "annual_cost": 20800, "hours_saved": 291.2, "cost_saved": 14560}


def mock_client(parsed_output=None, stop_reason="end_turn", error=None):
    client = MagicMock()
    if error:
        client.beta.messages.parse.side_effect = error
    else:
        client.beta.messages.parse.return_value = MagicMock(
            parsed_output=parsed_output, stop_reason=stop_reason
        )
    return client


def test_success_returns_insights_and_summary():
    narrative = Narrative(task_insights=["a", "b", "c"], summary="overall")
    client = mock_client(parsed_output=narrative)

    result = generate_narrative(TASKS, TOTALS, client=client)

    assert result == {"task_insights": ["a", "b", "c"], "summary": "overall"}


def test_makes_exactly_one_call_with_all_tasks():
    client = mock_client(parsed_output=Narrative(task_insights=["a", "b", "c"], summary="s"))

    generate_narrative(TASKS, TOTALS, client=client)

    client.beta.messages.parse.assert_called_once()
    sent = client.beta.messages.parse.call_args.kwargs["messages"][0]["content"]
    for task in TASKS:
        assert task["description"] in sent


def test_timeout_returns_none():
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    client = mock_client(error=anthropic.APITimeoutError(request=request))

    assert generate_narrative(TASKS, TOTALS, client=client) is None


def test_api_error_returns_none():
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx2.Response(500, request=request)
    client = mock_client(error=anthropic.InternalServerError("boom", response=response, body=None))

    assert generate_narrative(TASKS, TOTALS, client=client) is None


def test_missing_api_key_returns_none(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    assert generate_narrative(TASKS, TOTALS) is None


def test_refusal_returns_none():
    client = mock_client(parsed_output=None, stop_reason="refusal")

    assert generate_narrative(TASKS, TOTALS, client=client) is None


def test_wrong_number_of_insights_returns_none():
    client = mock_client(parsed_output=Narrative(task_insights=["only one"], summary="s"))

    assert generate_narrative(TASKS, TOTALS, client=client) is None
