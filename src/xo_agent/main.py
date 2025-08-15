# src/xo_agent/main.py
from fastapi import FastAPI
from xo_agent.webhooks.github import router as github_router

app = FastAPI(title="XO Agent")
app.include_router(github_router, prefix="")
