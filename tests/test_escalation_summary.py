from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_escalation_summary() -> None:
    response = client.post(
        "/escalation-summary",
        json={
            "issue_summary": "SaaS admin console login API returns persistent 403",
            "product_area": "SaaS Platform",
            "observed_error": "403 Forbidden, request_id=req_login_403_test",
            "business_impact": "Some enterprise users cannot access the admin console.",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["escalation_team"]
    assert body["required_information"]
    assert body["suggested_summary"]
