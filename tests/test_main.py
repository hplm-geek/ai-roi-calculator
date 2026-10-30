from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

TASK = {"description": "Invoice entry", "hours_per_occurrence": 2, "frequency": "weekly", "hourly_rate": 50}


def test_numbers_still_returned_when_claude_fails():
    with patch("main.generate_narrative", return_value=None):
        response = client.post("/api/calculate", json={"tasks": [TASK] * 3})

    assert response.status_code == 200
    body = response.json()
    assert body["narrative"] is None
    assert body["tasks"][0]["cost_saved"] == 3640.0
    assert body["totals"]["cost_saved"] == 10920.0


def test_rejects_fewer_than_three_tasks():
    assert client.post("/api/calculate", json={"tasks": [TASK] * 2}).status_code == 422


def test_rejects_more_than_five_tasks():
    assert client.post("/api/calculate", json={"tasks": [TASK] * 6}).status_code == 422
