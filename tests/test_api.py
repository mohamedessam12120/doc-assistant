import sys
import types

import pytest
from fastapi.testclient import TestClient

FAKE_RESULT = {
    "answer": "21 working days",
    "sources": [{"source": "leave_policy.pdf", "page": 1}],
    "top_distance": 0.3,
    "refused": False,
}


@pytest.fixture
def client(monkeypatch):
    # Replace the real "ask" module (Chroma + Ollama) with a fake one
    fake = types.ModuleType("ask")
    fake.ask_detailed = lambda q: FAKE_RESULT
    monkeypatch.setitem(sys.modules, "ask", fake)
    monkeypatch.setenv("DOC_ASSISTANT_API_KEY", "test-key")
    monkeypatch.syspath_prepend("src")
    sys.modules.pop("api", None)  # force a fresh import with the fake and the key
    import api

    return TestClient(api.app)


def post(client, key=None, question="How many days of leave?"):
    headers = {"x-api-key": key} if key is not None else {}
    return client.post("/ask", json={"question": question}, headers=headers)


def test_health_needs_no_key(client):
    assert client.get("/health").status_code == 200


def test_missing_key_is_rejected(client):
    assert post(client).status_code == 401


def test_wrong_key_is_rejected(client):
    assert post(client, key="wrong").status_code == 401


def test_valid_key_returns_answer(client):
    r = post(client, key="test-key")
    assert r.status_code == 200
    assert r.json()["answer"] == "21 working days"


def test_too_short_question_is_rejected(client):
    assert post(client, key="test-key", question="a").status_code == 422


def test_server_without_configured_key_rejects_everyone(monkeypatch, client):
    # Fail closed: no key configured on the server means nobody gets in
    monkeypatch.setenv("DOC_ASSISTANT_API_KEY", "")
    sys.modules.pop("api", None)
    import api

    assert TestClient(api.app).post(
        "/ask", json={"question": "hello there"}, headers={"x-api-key": ""}
    ).status_code == 401