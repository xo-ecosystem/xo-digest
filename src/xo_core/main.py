from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from xo_core.fab_tasks.utils.digest_preview import register_digest_preview_routes
from .push_logbook import push_logbook

app = FastAPI()

# Optional CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes (e.g., for digest preview)
register_digest_preview_routes(app)

@app.get("/")
def read_root():
    return {"XO": "Vault is Alive"}