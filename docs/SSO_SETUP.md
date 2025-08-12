XO SSO Setup (Zitadel-first)

Overview
Add first-class OIDC auth to XO Agent API and the /vault/ui page using Zitadel (or any OIDC IdP). Supports dual auth during migration:

- Preferred: Authorization: Bearer <OIDC access_token>
- Fallback (temporary): X-Agent-Secret: <secret>

Steps

1. Reserve login.xo.center → your IdP (Zitadel Cloud or self-hosted).
2. In Zitadel, create Project XO → Applications:
   - xo-pulse-ui (SPA/public)
     - PKCE only, no client secret
     - Redirect URIs: https://xo-pulse.com/vault/ui, http://localhost:8003/vault/ui
   - xo-agent-api (confidential, optional later)
     - Audience: api://xo-agent
   - Enable MFA, WebAuthn, and add role brie.
3. Set env variables:

XO_OIDC_ISSUER=https://login.xo.center
XO_OIDC_AUDIENCE=api://xo-agent
XO_OIDC_CLIENT_ID_SPA=xo-pulse-ui
XO_OIDC_REDIRECT_URI=https://xo-pulse.com/vault/ui
XO_CORS=https://xo-pulse.com
XO_ALLOW_LEGACY_SECRET=1

4. Migration: keep XO_ALLOW_LEGACY_SECRET=1 for a week, then set to 0.

Local Dev

- make serve-api
- Visit http://localhost:8003/vault/ui → Sign in → run a decode.
- Confirm requests carry Authorization: Bearer ...

Fly Deploy (recap)

fly secrets set \
 XO_OIDC_ISSUER=https://login.xo.center \
 XO_OIDC_AUDIENCE=api://xo-agent \
 XO_OIDC_CLIENT_ID_SPA=xo-pulse-ui \
 XO_OIDC_REDIRECT_URI=https://xo-pulse.com/vault/ui \
 XO_CORS=https://xo-pulse.com \
 XO_ALLOW_LEGACY_SECRET=1

Then deploy. Point xopulse.to/Brie → https://xo-pulse.com/vault/ui.

Next Pass (nice-to-haves)

- Token introspection + cache
- Role/scope gates per endpoint (e.g., brie can open burn-after-read)
- Add /start convenience at login.xo.center/start
- CI job to reject PRs that remove auth guards on /agent/\*

---

Zitadel Setup: XO (Click-path + JSON)

Click-path (screenshots to be added):

1. Create instance/org

   - Sign in to Zitadel Console → Create new Org (or use default).

2. Custom Domain (login.xo.center)

   - Settings → Custom Domains → Add → enter `login.xo.center` → Continue.
   - Follow DNS verification steps (TXT) until Verified. TLS will be provisioned.

3. Project

   - Projects → New → Name: `XO` → Create.

4. Application: SPA (xo-pulse-ui)

   - XO Project → Applications → New → Web.
   - Name: `xo-pulse-ui`
   - Client Type: Public
   - Authentication Method: Code + PKCE (S256)
   - Redirect URIs (dev): `http://localhost:8003/vault/ui`
   - Redirect URIs (prod): `https://xo-pulse.com/vault/ui`
   - Allowed Origins (CORS): `http://localhost:8003`, later add `https://xo-pulse.com`
   - Scopes: `openid`, `profile`, `email`, optionally `offline_access`
   - Save → copy the Client ID.

5. (Optional) Application: API (xo-agent)

   - XO Project → Applications → New → API / Resource Server.
   - Name: `xo-agent`
   - Audience/Identifier: `xo-agent` (or `api://xo-agent`).
   - Save.

6. Role (brie) and assignment

   - XO Project → Roles → New → Key: `brie`, Display: `Brie` → Create.
   - Members → Add → select Brie’s user → assign role `brie`.

7. Claims (optional mapping for roles)
   - XO Project → Applications → `xo-pulse-ui` → Token Settings.
   - Ensure ID/Access token include `preferred_username` and/or `email`.
   - If using roles in tokens, enable role claims or add a mapper so `roles: ["brie"]` appears.

JSON reference (export-like examples)

SPA client minimal:

```
{
  "name": "xo-pulse-ui",
  "type": "web",
  "public": true,
  "auth_method": "code_pkce",
  "redirect_uris": [
    "http://localhost:8003/vault/ui",
    "https://xo-pulse.com/vault/ui"
  ],
  "allowed_origins": [
    "http://localhost:8003",
    "https://xo-pulse.com"
  ],
  "scopes": ["openid", "profile", "email", "offline_access"]
}
```

API audience minimal:

```
{
  "name": "xo-agent",
  "type": "api",
  "audience": "xo-agent"
}
```

Env mapping used by the XO Agent:

```
XO_OIDC_ISSUER=https://login.xo.center
XO_OIDC_CLIENT_ID_SPA=xo-pulse-ui   # or XO_OIDC_CLIENT_ID if you prefer
XO_OIDC_REDIRECT_URI=http://localhost:8003/vault/ui
XO_OIDC_AUDIENCE=api://xo-agent     # optional until you enforce
XO_CORS=http://localhost:8003,https://xo-pulse.com
XO_WEB_ALLOWLIST=brie
XO_ALLOW_LEGACY_SECRET=0            # set 1 during migration
```

Verification checklist:

- `https://login.xo.center/.well-known/openid-configuration` returns Zitadel JSON.
- On `/vault/ui`, `window.XO` shows the issuer, clientId, and redirectUri.
- Sign in completes and shows “Signed in as …”.
- Decode requests carry `Authorization: Bearer <token>`.
- Reports gated to Brie per role or allowlist.

---

Fly Proxy (login.xo.center) quick setup

1. Fill these envs (local export or GH secrets for CI):

```
ZITADEL_ISSUER="https://<org>.zitadel.cloud"
ALLOWED_ORIGINS="http://localhost:8003,https://xo-pulse.com"
LOGIN_HOST="login.xo.center"
FLY_APP_NAME="xo-login-proxy"
```

2. Local deploy with Make:

```
make login-proxy-deploy \
  FLY_APP_NAME=$FLY_APP_NAME \
  LOGIN_HOST=$LOGIN_HOST \
  ZITADEL_ISSUER=$ZITADEL_ISSUER \
  ALLOWED_ORIGINS=$ALLOWED_ORIGINS
```

3. DNS:

- CNAME `login.xo.center` → `<app>.fly.dev` (exact hostname from Fly)

4. CI deploy (tag-based):

- Push tag `login-proxy-v1.0.0` and ensure repo secrets are set:
  - `FLY_API_TOKEN`, `LOGIN_PROXY_APP`, `LOGIN_PROXY_HOST`, `LOGIN_PROXY_ZITADEL_ISSUER`, `LOGIN_PROXY_ALLOWED_ORIGINS`
