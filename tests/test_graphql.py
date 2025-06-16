"""xo‑core main FastAPI entry‑point with a basic GraphQL endpoint."""

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# ─────────────────────────────────── GraphQL schema ──────────────────────────


@strawberry.type
class Query:
    """Root GraphQL query."""

    @strawberry.field
    def ping(self) -> str:
        """Simple liveness probe used in tests."""
        return "pong"


schema = strawberry.Schema(query=Query)

# ───────────────────────────────────── FastAPI app ────────────────────────────

app = FastAPI(title="XO Core API")

# Mount GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


# Plain REST health‑check (handy for infra)
@app.get("/health", tags=["utils"])
async def health() -> dict[str, str]:  # noqa: D401
    """Return service health."""
    return {"status": "ok"}
