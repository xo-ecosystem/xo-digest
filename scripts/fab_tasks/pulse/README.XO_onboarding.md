# 🌍 XO Pulse Onboarding Guide

Welcome to **XO Pulse** — your gateway to publishing time-locked, immutable, and community-powered updates in the XO ecosystem.

---

## 🧠 What is a Pulse?

A **pulse** is a markdown-based `.mdx` file containing your message, update, poem, call-to-action, or proposal. Every pulse can be:

- Created with a single command
- Signed to verify origin
- Synced to Arweave/IPFS for permanent storage
- Previewed in your browser
- Reacted to with comments

---

## ⚙️ CLI Usage (Power Users + Contributors)

XO Pulse is powered by Fabric tasks:

| Command                          | Description                             |
| -------------------------------- | --------------------------------------- |
| `xo-fab pulse.new:your_slug`     | Create a new pulse `.mdx` file          |
| `xo-fab pulse.preview:your_slug` | Render pulse as `.html` for preview     |
| `xo-fab pulse.publish:your_slug` | Upload to Arweave + IPFS + trigger sign |
| `xo-fab pulse.sync`              | Batch sync all pulses to Arweave        |
| `xo-fab pulse.sign:your_slug`    | Trigger signature service for a pulse   |
| `xo-fab pulse.clean`             | Remove `.txid` and `.preview` artifacts |

---

## 🔁 Typer CLI Companion (Optional)

We're adding a companion CLI for non-coders soon:

```bash
xo-pulse new "your_slug"
xo-pulse publish "your_slug"
xo-pulse preview "your_slug"
xo-pulse clean
```

This wraps Fabric with human-friendly commands. Stay tuned.

---

## 🖥️ Web Interface (WIP)

An upcoming SvelteKit + FastAPI UI will let you:

- 👩‍💻 Create and preview pulses
- ✍️ Edit or write markdown directly
- ☁️ Publish and get back Arweave/IPFS links
- 🧠 See signature status

📍Location: `http://localhost:3000` or deployed to XO-Node

---

## 📦 Requirements

- Python 3.9+
- Install once:
  ```bash
  pip install fabric invoke arweave-python-client markdown2
  ```

---

## 🗂 Pulse Directory Structure

```text
content/pulses/
  └── your_slug.mdx         # Your pulse content
  └── your_slug.mdx.txid    # Arweave transaction ID (auto)
.preview/
  └── your_slug.html        # Local HTML preview
.vault/
  └── txids/                # Mirror of all txids
  └── logbook.json          # Signed record of uploads
```

---

## 🚀 Let's Go

1. Run `xo-fab pulse.new:hello_xo`
2. Edit the file under `content/pulses/`
3. Preview with `xo-fab pulse.preview:hello_xo`
4. Publish using `xo-fab pulse.publish:hello_xo`
5. View your Arweave tx or IPFS CID
