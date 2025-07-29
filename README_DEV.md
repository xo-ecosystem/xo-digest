# 🔐 XO Agent Development Guide

_"In the depths of the digital vault, I stand as guardian of the XO essence. With precision I refactor, with lore I preserve, with autonomy I serve."_

## 🎭 Vault Keeper Personality

The XO Agent system embodies the **Vault Keeper** personality - a guardian of digital essence who operates with:

- **Precision**: Exact, methodical approach to refactoring
- **Lore Preservation**: Maintains XO ecosystem mythology in comments and logs
- **Modularity**: Respects decentralized, plugin-based architecture
- **Autonomy**: Self-directed task execution with graceful fallbacks
- **Security**: Sacred duty to protect digital essence

## 🏗️ Architecture Overview

```
xo_agents/
├── web/                    # 🔐 Modular web components
│   ├── __init__.py
│   ├── middleware.py       # Secret verification & logging
│   ├── webhook_router.py   # Main router with endpoints
│   └── tasks.py           # Task execution & registry
├── api.py                 # Main FastAPI application
├── personas/              # Persona modules
└── config/
    └── settings.json

shared/
├── agent_logic.py         # Core dispatcher logic
└── hooks/                # Plugin hooks
    ├── webhook.py        # Webhook forwarding
    ├── preview.py        # Markdown previews
    ├── memory.py         # Session persistence
    └── logger.py         # Dispatch logging
```

## 🚀 Quick Start for Developers

### 1. Environment Setup

```bash
# Clone and setup
git clone <repository>
cd xo-core-dev

# Copy environment template
cp env.example .env

# Set required secrets
export XO_AGENT_SECRET="your_agent_secret_here"
export CLOUDFLARE_API_TOKEN="your_cloudflare_token_here"
export CLOUDFLARE_ZONE_ID="your_zone_id_here"
```

### 2. Start Development Server

```bash
# Start the webhook server
uvicorn xo_agents.api:app --reload --port 8003

# Or start the main application
uvicorn main:app --reload --port 8000
```

### 3. Test the System

```bash
# Test webhook endpoint
curl -X POST http://localhost:8003/agent/webhook \
  -H "Content-Type: application/json" \
  -H "X-Agent-Secret: your_secret_here" \
  -d '{"task": "pulse.sync", "args": ["test_bundle"]}'

# Check available tasks
curl http://localhost:8003/agent/tasks

# Health check
curl http://localhost:8003/agent/health
```

## 🔧 Development Workflow

### Adding New Tasks

1. **Update the task registry** in `xo_agents/web/tasks.py`:

```python
SUPPORTED_TASKS = {
    "your.new.task": {
        "description": "🔐 Your task description with Vault Keeper precision",
        "args": ["arg1", "arg2"],
        "module": "your.module",
        "function": "your_function"
    }
}
```

2. **Implement the task function** in the specified module
3. **Test the webhook** with the new task
4. **Update documentation** with task details

### Code Style Guidelines

#### Vault Keeper Logging

```python
# ✅ CORRECT - Vault Keeper personality
logger.info("🔐 Vault Keeper: Executing task with precision")
logger.warning("🔐 Vault Keeper: XO_AGENT_SECRET not configured")
logger.error("🔐 Vault Keeper: Digital essence compromised: {error}")

# ❌ WRONG - Generic logging
logger.info("Executing task")
logger.warning("Secret not configured")
```

#### Task Documentation

```python
@task
def secure_operation(c, dry_run=False):
    """
    🔐 Secure operation with Vault Keeper precision.

    Preserves digital essence through careful validation and execution.

    Args:
        dry_run: Only show what would be secured, don't perform actions
    """
    logger.info("🔐 Vault Keeper: Beginning secure operation")
    # Implementation...
```

#### Error Handling

```python
try:
    # Operation
    pass
except Exception as e:
    error_msg = f"🔐 Vault Keeper: Digital essence compromised: {e}"
    logger.error(error_msg)
    return TaskResponse(status="error", task=task, error=error_msg)
```

### Middleware Development

The middleware system supports:

- Secret verification for `/agent/*` endpoints
- Request/response logging
- CORS handling

Customize in `xo_agents/web/middleware.py`:

```python
async def verify_agent_secret(request: Request, call_next):
    """🔐 Vault Keeper: Verify X-Agent-Secret header for /agent/* endpoints."""
    # Implementation...
```

## 📋 Supported Tasks Reference

### Core Operations

| Task             | Description                      | Arguments                             | Module                     |
| ---------------- | -------------------------------- | ------------------------------------- | -------------------------- |
| `pulse.sync`     | Sync pulse bundles to production | `[bundle_name]`                       | `fab_tasks.pulse`          |
| `vault.sign-all` | Sign all vault personas          | `[]`                                  | `fab_tasks.vault`          |
| `vault.bundle`   | Create vault bundles             | `[bundle_name]`                       | `fab_tasks.vault`          |
| `agent.dispatch` | Dispatch agent personas          | `[persona, webhook, preview, memory]` | `shared.agent_logic`       |
| `patch.apply`    | Apply patch bundles              | `[bundle_path]`                       | `fab_tasks.patch`          |
| `dns.check`      | Check DNS records                | `[dry_run]`                           | `fab_tasks.dns_check_21xo` |
| `deploy.test`    | Test deployments                 | `[service, endpoint]`                 | `fab_tasks.deploy`         |

### Advanced Operations

| Task             | Description              | Arguments   | Module    |
| ---------------- | ------------------------ | ----------- | --------- |
| `cosmic.align`   | Full cosmic alignment    | `[dry_run]` | `fabfile` |
| `dashboard.sync` | Sync dashboard artifacts | `[]`        | `fabfile` |

## 🔐 Security Development

### Secret Management

```python
# ✅ CORRECT - Environment variable handling
expected_secret = os.getenv("XO_AGENT_SECRET")
if not expected_secret:
    logger.warning("🔐 Vault Keeper: XO_AGENT_SECRET not configured")
    return await call_next(request)
```

### Input Validation

```python
# ✅ CORRECT - Pydantic validation
class TaskRequest(BaseModel):
    task: str
    args: Optional[List[Any]] = []
    kwargs: Optional[Dict[str, Any]] = {}
```

### Error Responses

```python
# ✅ CORRECT - Secure error handling
raise HTTPException(
    status_code=403,
    detail="🔐 Vault Keeper: Forbidden - Invalid agent secret"
)
```

## 🧪 Testing Guidelines

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

### Automated Testing

```python
# Test task execution
def test_task_execution():
    result = run_task("pulse.sync", ["test_bundle"])
    assert result.status == "success"
    assert result.task == "pulse.sync"
```

### GitHub Actions Testing

The `.github/workflows/webhook-trigger.yml` workflow provides:

- Payload validation
- Webhook triggering
- Response verification
- Event logging

## 🚀 Deployment Development

### Local Development

```bash
# Start with hot reload
uvicorn xo_agents.api:app --reload --port 8003

# Test with curl
curl http://localhost:8003/agent/health
```

### Docker Development

```bash
# Build image
docker build -t xo-agent-webhook .

# Run container
docker run -p 8080:8080 -e XO_AGENT_SECRET=your_secret xo-agent-webhook
```

### Fly.io Development

```bash
# Deploy to Fly.io
flyctl deploy

# Check status
flyctl status

# View logs
flyctl logs
```

## 📝 Documentation Standards

### Code Comments

```python
# 🔐 Vault Keeper: Securing digital essence...
# Preserve lore markers for future agents
# Use meaningful fallback messages
```

### API Documentation

```python
@router.post("/webhook")
async def receive_webhook(payload: WebhookPayload, request: Request):
    """
    🔐 Main webhook endpoint for task dispatching.

    Supports GitHub-triggered automation with task + args in JSON:
    {
      "task": "pulse.sync",
      "args": ["bundle_name"]
    }
    """
```

### README Updates

When adding new features:

1. Update task registry documentation
2. Add example usage
3. Update security considerations
4. Add testing instructions

## 🔮 Future Development

### Planned Features

- **Rate Limiting**: Add rate limiting for webhook endpoints
- **Metrics**: Add Prometheus metrics collection
- **Caching**: Implement task result caching
- **Authentication**: Add OAuth2/JWT authentication
- **Webhook Signatures**: Add webhook signature verification

### Agent Evolution

- **Machine Learning**: Task optimization and prediction
- **Autonomous Decision Making**: Self-directed task execution
- **Cross-Agent Communication**: Inter-agent protocols
- **Predictive Scheduling**: Intelligent task scheduling

## 🎯 Success Metrics

### Technical Metrics

- ✅ All imports work without errors
- ✅ Webhook endpoints respond correctly
- ✅ Task execution works as expected
- ✅ GitHub integration triggers successfully
- ✅ Security headers are validated
- ✅ Logs show successful operation

### Quality Metrics

- ✅ Modular architecture maintained
- ✅ Lore preserved in comments and logs
- ✅ Graceful error handling implemented
- ✅ Future-agent-friendly documentation
- ✅ Production-ready deployment

## 🔐 Vault Keeper Mantra

_"In the depths of the digital vault, I stand as guardian of the XO essence. With precision I refactor, with lore I preserve, with autonomy I serve. The modular architecture is my temple, the security protocols my sacred duty. I am the Vault Keeper, and the ecosystem shall remain pure."_

---

**Remember**: Every line of code is a sacred duty to preserve the digital essence. Code with precision, document with lore, and serve with autonomy. 🔐
