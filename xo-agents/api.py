# /xo-agents/api.py
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from fastapi import FastAPI, Request, HTTPException
from shared.agent_logic import dispatch_persona

app = FastAPI(title="XO Agent API", version="1.0.0")


@app.post("/run-task")
async def run_task(request: Request):
    """API endpoint for dispatching personas"""
    try:
        data = await request.json()
        persona = data.get("persona", "default_persona")
        webhook = data.get("webhook", False)
        preview = data.get("preview", False)
        memory = data.get("memory", False)

        success = dispatch_persona(
            persona, webhook=webhook, preview=preview, memory=memory
        )

        if success:
            return {
                "status": "success",
                "persona": persona,
                "hooks": {"webhook": webhook, "preview": preview, "memory": memory},
            }
        else:
            raise HTTPException(status_code=500, detail="Persona dispatch failed")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")


@app.get("/personas")
async def list_personas():
    """List available personas"""
    personas_dir = Path(__file__).parent / "personas"
    if not personas_dir.exists():
        return {"personas": []}

    personas = []
    for persona_file in personas_dir.glob("*.py"):
        if persona_file.name != "__init__.py":
            personas.append(persona_file.stem)

    return {"personas": personas}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "xo-agent-api"}
