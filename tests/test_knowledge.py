from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_knowledge_status() -> None:
    response = client.get("/knowledge/status")

    body = response.json()
    assert response.status_code == 200
    assert "document_count" in body
    assert "chunk_size" in body
    assert body["mode"] in {"keyword_fallback", "chroma"}


def test_knowledge_search_without_external_key() -> None:
    response = client.post(
        "/knowledge/search",
        json={
            "query": "企业知识库问答结果不准确，应该如何排查？",
            "top_k": 4,
            "include_deprecated": False,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["mode"] in {"keyword_fallback", "chroma"}
    assert "results" in body
    assert isinstance(body["results"], list)
