from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_log_analyze_504() -> None:
    response = client.post(
        "/log-analyze",
        json={
            "log_text": 'status=504 request_time=60.001 upstream_response_time=60.000 error="upstream timed out" request_id=req_504_test',
            "question": "Why did this API return 504?",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert 504 in body["detected_status_codes"]
    assert body["status_code_explanation"]
    assert body["troubleshooting_suggestions"]
