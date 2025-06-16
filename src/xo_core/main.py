# File: src/xo_core/main.py
"""xo_core FastAPI application with a basic Strawberry GraphQL endpoint.

The module exposes the variable `app`, which is what tests import.
"""

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# --------------------------------------------------------------------------- #
# GraphQL schema
# --------------------------------------------------------------------------- #


@strawberry.type
class Query:
    """Root GraphQL query."""

    @strawberry.field
    def hello(self) -> str:  # noqa: D401 – "say hello" is fine.
        """Return a friendly greeting."""
        return "Hello, world!"


schema = strawberry.Schema(query=Query)

# --------------------------------------------------------------------------- #
# FastAPI application
# --------------------------------------------------------------------------- #

app = FastAPI(title="xo-core API")

# Mount the GraphQL endpoint (path expected by tests: `/graphql`)
app.include_router(GraphQLRouter(schema), prefix="/graphql")


# Optional health‑check route for future extensions
@app.get("/health", tags=["meta"])
def health_check() -> dict[str, str]:
    """Simple liveness probe."""
    return {"status": "ok"}


# File: src/xo_core/__init__.py
""
