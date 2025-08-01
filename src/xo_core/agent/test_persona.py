from fastapi.testclient import TestClient
from xo_core.agent.agent_game import AgentGame

app = AgentGame().app
client = TestClient(app)


def test_dispatch():
    for persona in ["vault_keeper", "scribe"]:
        for event in ["ping", "status"]:
            payload = {
                "persona": persona,
                "event": event,
                "payload": {"test": "xo-ping"},
            }
            response = client.post("/agent/persona/dispatch", json=payload)
            print(
                f"RESPONSE {persona}:{event} →", response.status_code, response.json()
            )


if __name__ == "__main__":
    test_dispatch()
