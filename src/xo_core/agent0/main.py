from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "ok"}


class Persona(BaseModel):
    name: str
    description: str = ""
    traits: list[str] = []
    prompt: str = ""


@app.post("/personas")
def create_persona(payload: Persona, request: Request):
    print("🚀 Received persona:", payload.dict())
    return {"status": "success", "name": payload.name}
