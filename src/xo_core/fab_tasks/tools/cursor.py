import json
import os
import socket

from invoke import task, Collection

MCP_PATH = ".cursor/mcp.json"

OLLAMA_CONFIG = {
    "model": "ollama/llama3",
    "contextStrategy": "smart",
    "features": {
        "code_completion": True,
        "inline_assist": True,
        "natural_language_editing": True,
    },
    "providers": {"ollama": {"baseUrl": "http://localhost:11434", "model": "llama3"}},
    "promptPrefix": "You are a local XO-agent running from Ollama. Prioritize speed, clarity, and minimalism.",
}

OPENAI_CONFIG = {
    "model": "gpt-4",
    "contextStrategy": "smart",
    "features": {
        "code_completion": True,
        "inline_assist": True,
        "natural_language_editing": True,
    },
    "providers": {"openai": {"apiKey": "${OPENAI_API_KEY}", "model": "gpt-4"}},
    "promptPrefix": "You are a cloud-based XO-agent. Write clean, secure, and humanity-first code for XO ecosystem.",
}


def save_mcp(config):
    os.makedirs(".cursor", exist_ok=True)
    with open(MCP_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Updated {MCP_PATH}")


def is_ollama_running(host="localhost", port=11434):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        return False


@task
def switch(c, mode="ollama"):
    """
    🧠 Switch .cursor/mcp.json between Ollama and OpenAI
    Usage: xo-fab tools.cursor.switch:ollama or :openai
    """
    if mode == "ollama":
        if is_ollama_running():
            save_mcp(OLLAMA_CONFIG)
            print("🦙 Switched to Ollama (llama3)")
        else:
            print("⚠️ Ollama not running on port 11434. Aborting.")
    elif mode == "openai":
        save_mcp(OPENAI_CONFIG)
        print("☁️ Switched to OpenAI (gpt-4)")
    else:
        print("❓ Invalid mode. Use: ollama or openai")


# Create namespace
ns = Collection("cursor")
ns.add_task(switch)
