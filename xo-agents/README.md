# XO Agents - Plugin-Based Persona Dispatcher

A modular, plugin-based system for dispatching XO personas with support for CLI and API interfaces.

## Architecture

```
xo-agents/
├── agent_cli.py          # CLI interface using invoke
├── api.py               # FastAPI interface
├── personas/            # Persona modules
│   ├── seal_dream.py    # Example persona
│   └── default_persona.py
└── config/
    └── settings.json    # Default settings

shared/
├── agent_logic.py       # Core dispatcher logic
└── hooks/              # Plugin hooks
    ├── webhook.py      # Webhook forwarding
    ├── preview.py      # Markdown previews
    ├── memory.py       # Session persistence
    └── logger.py       # Dispatch logging
```

## Usage

### CLI Interface

```bash
# List available personas
fab -f xo-agents/agent_cli.py list_personas

# Dispatch a persona
fab -f xo-agents/agent_cli.py dispatch_persona_cli --persona=seal_dream --webhook --preview --memory

# Use defaults from config/settings.json
fab -f xo-agents/agent_cli.py dispatch_persona_cli
```

### API Interface

```bash
# Start the API server
uvicorn xo-agents.api:app --reload --port 8003

# Dispatch via API
curl -X POST http://localhost:8003/run-task \
  -H "Content-Type: application/json" \
  -d '{"persona": "seal_dream", "webhook": true, "preview": true, "memory": true}'

# List personas
curl http://localhost:8003/personas

# Health check
curl http://localhost:8003/health
```

## Creating Personas

Add new personas to `xo-agents/personas/`:

```python
# xo-agents/personas/my_persona.py
def run():
    """My custom persona"""
    print("🎭 My persona is running!")
    return "Custom persona content"
```

## Plugin Hooks

The system supports plugin hooks that execute based on flags:

- **webhook**: Sends dispatch events to configured webhook URL
- **preview**: Generates Markdown previews in `public/previews/`
- **memory**: Persists session data in `.memory/`
- **logger**: Logs all dispatches to `logs/agent_dispatches.log`

### Environment Variables

- `XO_AGENT_WEBHOOK_URL`: Webhook endpoint URL (default: webhook.site placeholder)

## Error Handling

- Unknown personas fall back to `default_persona`
- Hook failures are logged but don't stop execution
- CLI returns exit code 1 on dispatch failure
- API returns appropriate HTTP status codes
