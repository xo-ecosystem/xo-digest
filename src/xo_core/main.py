import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from xo_agents.api import app as webhook_router

log = logging.getLogger(__name__)

app = FastAPI()

# Optional CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only register agent webhook for now
app.mount("/agent", webhook_router)


@app.get("/")
def read_root():
    return {"XO": "Webhook is alive"}
