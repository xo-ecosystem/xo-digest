// Cloudflare Worker: /webhook/sanity for xo-digest.com
export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    const webhookSecret = env.SANITY_WEBHOOK_SECRET || 'xo_sanity_default';
    const headers = Object.fromEntries(request.headers.entries());
    const rawBody = await request.text();


    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(webhookSecret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    const signatureHeader = headers['x-sanity-signature'];
    if (!signatureHeader) {
      return new Response('Missing signature header', { status: 400 });
    }

    const valid = await crypto.subtle.verify(
      'HMAC',
      cryptoKey,
      Uint8Array.from(atob(signatureHeader), c => c.charCodeAt(0)),
      new TextEncoder().encode(rawBody)
    );

    if (!valid) {
      return new Response('Invalid signature', { status: 401 });
    }

    try {
      const payload = JSON.parse(rawBody);
      const type = payload?._type || 'unknown';
      const id = payload?._id || 'none';

      console.log(`[Webhook] Received ${type} update: ${id}`);

      // Relay to main handler or fallback with logging
      const relayRes = await fetch(env.XO_DIGEST_RELAY_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: rawBody
      });

      if (!relayRes.ok && env.XO_DIGEST_RELAY_FALLBACK_URL) {
        // Fallback relay
        await fetch(env.XO_DIGEST_RELAY_FALLBACK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: rawBody
        });

        // Optional: Discord log hook
        if (env.XO_DIGEST_LOG_HOOK) {
          await fetch(env.XO_DIGEST_LOG_HOOK, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              content: `⚠️ Relay failure on ${new Date().toISOString()}`,
              embeds: [{
                title: "Relay Status",
                description: `Relay to \`${env.XO_DIGEST_RELAY_URL}\` failed, fallback triggered.`,
                color: 0xffcc00,
                footer: { text: "XO Digest Webhook" },
                timestamp: new Date().toISOString()
              }]
            })
          });
        }
        // Optional: Telegram alert
        if (env.XO_DIGEST_TELEGRAM_HOOK_URL) {
          await fetch(env.XO_DIGEST_TELEGRAM_HOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: `⚠️ *XO Digest Relay Fallback Triggered*\n\nRelay to \`${env.XO_DIGEST_RELAY_URL}\` failed.\n\n*Payload Type:* ${type}\n*ID:* ${id}\n*Time:* ${new Date().toISOString()}`,
              parse_mode: "Markdown"
            })
          });
        }
      }

      // Optional: markdown preview (stub)
      // const markdownPreview = renderMarkdownPreview(payload); // Implement if needed

      // Optional: queue IPFS upload (mock, non-blocking)
      if (env.XO_DIGEST_IPFS_UPLOAD_URL) {
        fetch(env.XO_DIGEST_IPFS_UPLOAD_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: rawBody
        }).catch(err => console.warn('[IPFS Upload Error]', err));
      }

      return new Response('✅ Received webhook', { status: 200 });
    } catch (err) {
      console.error('[Webhook Error]', err);
      return new Response('Invalid JSON', { status: 400 });
    }
  },
};