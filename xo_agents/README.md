# XO Agents - Modular Webhook System

A production-ready, modular FastAPI webhook system for XO agent task dispatching with GitHub integration.

## 🏗️ Architecture

```
xo_agents/
├── web/                    # Modular web components
│   ├── __init__.py
│   ├── middleware.py       # Secret verification & logging
│   ├── webhook_router.py   # Main router with endpoints
│   └── tasks.py           # Task execution & registry
├── api.py                 # Main FastAPI application
├── personas/              # Persona modules
│   ├── seal_dream.py
│   └── default_persona.py
└── config/
    └── settings.json
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Set required secrets
export XO_AGENT_SECRET="your_secret_here"
export CLOUDFLARE_API_TOKEN="your_token_here"
export CLOUDFLARE_ZONE_ID="your_zone_id_here"
```

### 2. Start the API Server

```bash
# Start the webhook server
uvicorn xo_agents.api:app --reload --port 8003

# Or start the main application
uvicorn main:app --reload --port 8000
```

### 3. Test the Webhook

```bash
# Test the webhook endpoint
curl -X POST http://localhost:8003/agent/webhook \
  -H "Content-Type: application/json" \
  -H "X-Agent-Secret: your_secret_here" \
  -d '{"task": "pulse.sync", "args": ["test_bundle"]}'

# Check available tasks
curl http://localhost:8003/agent/tasks

# Health check
curl http://localhost:8003/agent/health
```

## 📋 Available Tasks

The webhook system supports the following tasks:

| Task             | Description                     | Arguments                             |
| ---------------- | ------------------------------- | ------------------------------------- |
| `pulse.sync`     | Sync pulse bundle to production | `[bundle_name]`                       |
| `vault.sign-all` | Sign all vault personas         | `[]`                                  |
| `vault.bundle`   | Create vault bundle             | `[bundle_name]`                       |
| `agent.dispatch` | Dispatch agent persona          | `[persona, webhook, preview, memory]` |
| `patch.apply`    | Apply patch bundle              | `[bundle_path]`                       |
| `dns.check`      | Check DNS records               | `[dry_run]`                           |
| `deploy.test`    | Test deployment                 | `[service, endpoint]`                 |

## 🔗 GitHub Integration

### Manual Trigger

Use GitHub Actions to manually trigger webhooks:

1. Go to Actions → 🔗 Webhook Trigger
2. Click "Run workflow"
3. Select task and arguments
4. Execute

### Repository Dispatch

Trigger webhooks programmatically:

```bash
curl -X POST https://api.github.com/repos/your-username/your-repo/dispatches \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -d '{
    "event_type": "webhook-trigger",
    "client_payload": {
      "task": "pulse.sync",
      "args": ["my_bundle"],
      "webhook_url": "https://vault.21xo.com/agent/webhook"
    }
  }'
```

## 🔐 Security

### Secret Verification

All `/agent/*` endpoints require the `X-Agent-Secret` header:

```bash
curl -H "X-Agent-Secret: your_secret_here" \
  http://localhost:8003/agent/webhook
```

### Environment Variables

Required secrets:

- `XO_AGENT_SECRET`: Webhook authentication secret
- `CLOUDFLARE_API_TOKEN`: DNS management (optional)
- `CLOUDFLARE_ZONE_ID`: DNS zone ID (optional)

## 📊 API Endpoints

### Webhook Endpoints

| Endpoint          | Method | Description                                       |
| ----------------- | ------ | ------------------------------------------------- |
| `/agent/webhook`  | POST   | Main webhook for task dispatching                 |
| `/agent/test`     | GET    | Health check with available tasks                 |
| `/agent/tasks`    | GET    | List all available tasks                          |
| `/agent/health`   | GET    | Service health check                              |
| `/agent/echo`     | POST   | Debug endpoint for payload testing                |
| `/agent/run-task` | POST   | Alternative task execution with detailed response |

### Example Requests

```bash
# Basic webhook
curl -X POST http://localhost:8003/agent/webhook \
  -H "Content-Type: application/json" \
  -H "X-Agent-Secret: your_secret" \
  -d '{"task": "pulse.sync", "args": ["bundle_name"]}'

# Echo for debugging
curl -X POST http://localhost:8003/agent/echo \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": "payload"}}'

# Get available tasks
curl http://localhost:8003/agent/tasks
```

## 🔧 Development

### Adding New Tasks

1. **Update the task registry** in `xo_agents/web/tasks.py`:

```python
SUPPORTED_TASKS = {
    "your.new.task": {
        "description": "Description of your task",
        "args": ["arg1", "arg2"],
        "module": "your.module",
        "function": "your_function"
    }
}
```

2. **Implement the task function** in the specified module
3. **Test the webhook** with the new task

### Middleware Customization

The middleware system supports:

- Secret verification for `/agent/*` endpoints
- Request/response logging
- CORS handling

Customize in `xo_agents/web/middleware.py`.

## 📝 Logging

The system provides detailed logging for:

- Webhook requests and responses
- Task execution status
- Error handling
- Security events

Logs are written to stdout and can be configured via `LOG_LEVEL`.

## 🧪 Testing

### Manual Testing

```bash
# Test webhook endpoint
curl -X POST http://localhost:8003/agent/webhook \
  -H "Content-Type: application/json" \
  -H "X-Agent-Secret: your_secret" \
  -d '{"task": "agent.dispatch", "args": ["seal_dream", true, false, false]}'

# Test health endpoint
curl http://localhost:8003/agent/health

# Test task listing
curl http://localhost:8003/agent/tasks
```

### GitHub Actions Testing

The `.github/workflows/webhook-trigger.yml` workflow provides:

- Payload validation
- Webhook triggering
- Response verification
- Event logging

## 🚀 Production Deployment

### Environment Setup

1. Set all required environment variables
2. Configure secrets in your deployment platform
3. Set up proper logging and monitoring

### Security Checklist

- [ ] `XO_AGENT_SECRET` is set and secure
- [ ] HTTPS is enabled
- [ ] Rate limiting is configured
- [ ] Monitoring is set up
- [ ] Logs are being collected

### Monitoring

Monitor these endpoints:

- `/agent/health` - Service health
- `/agent/test` - Task availability
- Webhook response times
- Error rates

---

## 🎯 Success Indicators

You'll know the system is working when:

- ✅ Webhook endpoints respond correctly
- ✅ Tasks execute without errors
- ✅ GitHub integration triggers successfully
- ✅ Security headers are validated
- ✅ Logs show successful task execution

The system is now **production-ready** and supports ongoing GitHub-triggered automation! 🚀
