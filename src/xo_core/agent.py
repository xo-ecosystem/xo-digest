from typing import Any

def dispatch_payload(payload: dict) -> str:
    return f"🧠 Agent dispatched payload with keys: {list(payload.keys())}"

class Agent:
    def __init__(self, name: str = "XO-Agent", persona: str = "neutral"):
        self.name = name
        self.persona = persona

    # 🔌 API dispatcher logic
    def dispatch(self, payload: dict) -> dict:
        return {
            "agent": self.name,
            "persona": self.persona,
            "response": f"Echoed payload: {payload}"
        }

    # 🧠 Persona prompt responder
    def respond(self, prompt: str) -> str:
        return f"{self.persona.title()} {self.name} replies: {prompt}"

    # 🕹 Game-playing logic (Connect Four stub)
    def make_move(self, board: list[list[int]]) -> tuple[int, int]:
        for col in range(len(board[0])):
            if board[0][col] == 0:
                return (0, col)
        return (-1, -1)
