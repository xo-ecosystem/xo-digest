#!/bin/bash

CURSOR_MCP=".cursor/mcp.json"

USE_OLLAMA='{
  "model": "ollama/llama3",
  "contextStrategy": "smart",
  "features": {
    "code_completion": true,
    "inline_assist": true,
    "natural_language_editing": true
  },
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434",
      "model": "llama3"
    }
  },
  "promptPrefix": "You are a local XO-agent running from Ollama. Prioritize speed, clarity, and minimalism."
}'

USE_OPENAI='{
  "model": "gpt-4",
  "contextStrategy": "smart",
  "features": {
    "code_completion": true,
    "inline_assist": true,
    "natural_language_editing": true
  },
  "providers": {
    "openai": {
      "apiKey": "${OPENAI_API_KEY}",
      "model": "gpt-4"
    }
  },
  "promptPrefix": "You are a cloud-based XO-agent. Write clean, secure, and humanity-first code for XO ecosystem."
}'

if [ "$1" == "ollama" ]; then
  echo "$USE_OLLAMA" > "$CURSOR_MCP"
  echo "🔁 Switched Cursor to Ollama (llama3)"
elif [ "$1" == "openai" ]; then
  echo "$USE_OPENAI" > "$CURSOR_MCP"
  echo "☁️ Switched Cursor to OpenAI (gpt-4)"
else
  echo "Usage: $0 [ollama|openai]"
fi
