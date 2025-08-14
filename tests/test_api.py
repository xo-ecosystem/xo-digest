import json
from fastapi.testclient import TestClient
from xo_core.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("app") == "xo-core"
    assert body.get("status") == "ok"


def test_message_bottle_status():
    r = client.get("/message-bottle")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_message_bottle_publish():
    r = client.post("/message-bottle/publish", json={"hello": "world"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_digest_publish():
    payload = {"title": "Hello", "content": "World"}
    r = client.post("/digest/publish", data=json.dumps(payload))
    if r.status_code == 422:
        r = client.post("/digest/publish", json=payload)
    assert r.status_code == 200
    assert r.json() == {"ok": True}
