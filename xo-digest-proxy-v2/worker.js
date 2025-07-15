export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)
    const AUTH_HEADER = request.headers.get("xo-digest-verify-secret");
    const EXPECTED_SECRET = env.XO_DIGEST_VERIFY_SECRET;
    if (AUTH_HEADER !== EXPECTED_SECRET) {
      return new Response("🔒 Unauthorized", { status: 401 });
    }
    if (url.pathname === "/webhook/digest") {
      // Ping your internal endpoint (e.g. GitHub Actions, API Gateway, etc.)
      const triggerURL = "https://xo-core.pages.dev/api/trigger-digest" // Replace with your real endpoint
      const resp = await fetch(triggerURL, { method: "POST" })

      return new Response("✅ Digest webhook triggered!", {
        status: resp.ok ? 200 : 500,
      })
    }

    return new Response("❌ Not Found", { status: 404 })
  }
}
