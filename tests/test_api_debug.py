from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_api_debug_429() -> None:
    response = client.post(
        "/api-debug",
        json={
            "method": "POST",
            "url": "https://api.example.com/v1/chat/completions",
            "status_code": 429,
            "error_message": "Too Many Requests: rate limit exceeded for current workspace.",
            "request_id": "req_test_429",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["problem_type"] == "rate_limited"
    assert "429" in body["issue_summary"]
    assert body["troubleshooting_steps"]
