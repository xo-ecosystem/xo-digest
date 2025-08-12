import os
import time
from typing import Optional, Dict, Any, Tuple

import httpx
from jose import jwt
from fastapi import Request, HTTPException


ISSUER = os.getenv("XO_OIDC_ISSUER")  # e.g., https://login.xo.center
AUD = os.getenv(
    "XO_OIDC_AUDIENCE", ""
)  # expected aud, or comma-list (e.g., api://xo-agent)
ALLOW_X_AGENT_SECRET = os.getenv("XO_ALLOW_LEGACY_SECRET", "1") == "1"
LEGACY_SECRET = os.getenv("XO_AGENT_SECRET", "")
JWKS_CACHE_TTL = int(os.getenv("XO_OIDC_JWKS_TTL", "300"))

_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


async def _fetch_json(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


async def _get_jwks() -> Dict[str, Any]:
    now = time.time()
    cached = _cache.get("jwks")
    if cached and now - cached[0] < JWKS_CACHE_TTL:
        return cached[1]

    # Discover jwks_uri from OIDC discovery
    if not ISSUER:
        raise HTTPException(status_code=503, detail="OIDC not configured")
    discovery = await _fetch_json(
        ISSUER.rstrip("/") + "/.well-known/openid-configuration"
    )
    jwks_uri = discovery.get("jwks_uri")
    if not jwks_uri:
        # Zitadel fallback
        jwks_uri = ISSUER.rstrip("/") + "/oauth/v2/keys"
    jwks = await _fetch_json(jwks_uri)
    _cache["jwks"] = (now, jwks)
    return jwks


def _roles_from_claims(claims: Dict[str, Any]) -> list[str]:
    # Prefer simple 'roles'. Fallbacks for common IdPs.
    if "roles" in claims and isinstance(claims["roles"], list):
        return list(map(str, claims["roles"]))
    # Keycloak-ish:
    try:
        return list(map(str, claims["realm_access"]["roles"]))
    except Exception:
        pass
    # Zitadel project role mapping may be custom; accept empty if not present.
    return []


def _aud_ok(aud_claim: Any, expect: set[str]) -> bool:
    if not expect:
        return True
    if isinstance(aud_claim, str):
        return aud_claim in expect
    if isinstance(aud_claim, list):
        return any(a in expect for a in aud_claim)
    return False


async def verify_request(request: Request) -> Dict[str, Any]:
    # Legacy header?
    if ALLOW_X_AGENT_SECRET and LEGACY_SECRET:
        xs = request.headers.get("x-agent-secret") or request.headers.get(
            "X-Agent-Secret"
        )
        if xs and xs == LEGACY_SECRET:
            return {"sub": "legacy-secret", "roles": ["founder"], "auth": "secret"}

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = auth.split(" ", 1)[1].strip()
    jwks = await _get_jwks()
    try:
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token header")

    # Build key set for jose
    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            key = k
            break
    if not key:
        # refresh once if kid unknown
        _cache.pop("jwks", None)
        jwks = await _get_jwks()
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                key = k
                break
    if not key:
        raise HTTPException(status_code=401, detail="jwks key not found")

    try:
        claims = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256"), "RS256", "ES256", "PS256"],
            issuer=ISSUER.rstrip("/") if ISSUER else None,
            options={"verify_aud": False},
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"token verification failed: {e}")

    expect = set([a.strip() for a in AUD.split(",") if a.strip()])
    if not _aud_ok(claims.get("aud"), expect):
        raise HTTPException(status_code=401, detail="audience mismatch")

    roles = _roles_from_claims(claims)
    return {
        "sub": claims.get("sub", ""),
        "roles": roles,
        "auth": "oidc",
        "claims": claims,
    }
