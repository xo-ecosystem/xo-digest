

from fastapi import FastAPI
from xo_digest.webhook.relay import ipfs

app = FastAPI()

# Include the /api/ipfs-upload route
app.include_router(ipfs.router)