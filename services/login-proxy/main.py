import os
from urllib.parse import urljoin
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

UPSTREAM = os.getenv("ZITADEL_ISSUER", "").rstrip("/") + "/"
PUBLIC_ISSUER = f"https://{os.getenv('LOGIN_HOST','login.xo.center')}/"
ALLOWED = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app = FastAPI(title="XO Login Proxy")

# Serve optional branding under /brand/*
brand_dir = os.path.join(os.path.dirname(__file__), "brand")
if not os.path.isdir(brand_dir):
    os.makedirs(brand_dir, exist_ok=True)
app.mount("/brand", StaticFiles(directory=brand_dir), name="brand")

SECURITY_HEADERS = {
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # allow our UI to call this proxy
    "Access-Control-Allow-Credentials": "true",
}


def add_cors(resp: Response, origin: str | None):
    if origin and origin in ALLOWED:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"


@app.middleware("http")
async def security_mw(request: Request, call_next):
    resp = await call_next(request)
    for k, v in SECURITY_HEADERS.items():
        if k not in resp.headers:
            resp.headers[k] = v
    add_cors(resp, request.headers.get("Origin"))
    return resp


@app.options("/{path:path}")
async def preflight(path: str, request: Request):
    origin = request.headers.get("Origin")
    resp = Response(status_code=204)
    add_cors(resp, origin)
    resp.headers["Access-Control-Allow-Headers"] = "authorization,content-type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


def _rewrite_discovery(d: dict) -> dict:
    # rewrite all issuer-derived endpoints to our vanity domain
    def repl(val: str) -> str:
        if isinstance(val, str) and val.startswith(UPSTREAM):
            return PUBLIC_ISSUER + val[len(UPSTREAM) :]
        return val

    out = {}
    for k, v in d.items():
        if isinstance(v, list):
            out[k] = [repl(x) for x in v]
        else:
            out[k] = repl(v)
    return out


@app.get("/.well-known/openid-configuration")
async def discovery():
    async with httpx.AsyncClient(timeout=10) as cx:
        r = await cx.get(urljoin(UPSTREAM, "/.well-known/openid-configuration"))
        r.raise_for_status()
        data = r.json()
    data = _rewrite_discovery(data)
    data["issuer"] = PUBLIC_ISSUER.rstrip("/")
    return JSONResponse(data)


@app.get("/oauth/{rest:path}")
@app.post("/oauth/{rest:path}")
@app.get("/oidc/{rest:path}")
@app.post("/oidc/{rest:path}")
async def passthrough(rest: str, request: Request):
    # forward to upstream, keep method/query/body/headers sane
    upstream_url = urljoin(UPSTREAM, request.url.path.lstrip("/"))
    if request.url.query:
        upstream_url += f"?{request.url.query}"
    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length", "accept-encoding"}
    }
    body = await request.body()
    async with httpx.AsyncClient(timeout=30) as cx:
        r = await cx.request(
            request.method, upstream_url, headers=headers, content=body
        )
    resp = Response(content=r.content, status_code=r.status_code)
    for k, v in r.headers.items():
        if k.lower() not in {
            "content-length",
            "transfer-encoding",
            "content-encoding",
            "connection",
        }:
            resp.headers[k] = v
    for k, v in SECURITY_HEADERS.items():
        resp.headers.setdefault(k, v)
    add_cors(resp, request.headers.get("Origin"))
    return resp


@app.get("/")
async def index():
    html = f"""
    <html><body style="font-family: ui-sans-serif; padding: 24px;">
      <h2>XO Login Proxy</h2>
      <p>Issuer: <code>{PUBLIC_ISSUER.rstrip('/')}</code></p>
      <p>Upstream: <code>{UPSTREAM.rstrip('/')}</code></p>
      <ul>
        <li><a href="/.well-known/openid-configuration">.well-known/openid-configuration</a></li>
        <li><a href="/brand">/brand (static branding)</a></li>
      </ul>
    </body></html>"""
    return HTMLResponse(html)
