# 🔐 XO Agent Deployment Guide

_"In the depths of the digital vault, I stand as guardian of the XO essence. With precision I deploy, with lore I preserve, with autonomy I serve."_

## ✅ **Pre-Deployment Checklist**

### **1. System Validation**

```bash
# Run comprehensive tests
python test_xo_agent.py

# Expected output: All 5/5 tests passed
```

### **2. Environment Configuration**

Ensure `.env.production` contains:

```bash
# Required for webhook security
XO_AGENT_SECRET=your_agent_secret_here

# Optional: GitHub integration
GITHUB_TOKEN=your_github_token_here

# Optional: Fly.io deployment
FLY_API_TOKEN=your_fly_token_here

# Optional: Webhook URL
XO_AGENT_WEBHOOK_URL=https://vault.21xo.com/agent/webhook
```

### **3. Repository Setup**

```bash
# Ensure you're on the correct branch
git branch
# Should show: main

# Check remote repository
git remote -v
# Should point to: xo-verses/xo-agent
```

## 🚀 **Deployment Options**

### **Option 1: Automated Deployment Script**

```bash
# Run the deployment script
python deploy_xo_agent.py

# This will:
# 1. Commit changes to GitHub
# 2. Trigger deployment via webhook
# 3. Provide deployment status
```

### **Option 2: Manual GitHub Actions**

1. Go to GitHub: https://github.com/xo-verses/xo-agent
2. Navigate to Actions → 🔗 Webhook Trigger
3. Click "Run workflow"
4. Select task: `cosmic.align`
5. Set args: `["false"]` (dry_run=false)
6. Click "Run workflow"

### **Option 3: Direct Fly.io Deployment**

```bash
# Set Fly.io token
export FLY_API_TOKEN=your_fly_token_here

# Deploy directly
flyctl deploy --app xo-agent
```

## 🔧 **Deployment Script Usage**

### **Environment Variables**

```bash
# Set deployment method
export DEPLOYMENT_METHOD=webhook    # or 'github' or 'fly'

# Run deployment
python deploy_xo_agent.py
```

### **Deployment Methods**

- **`webhook`**: Triggers webhook endpoint directly
- **`github`**: Uses GitHub Actions workflow
- **`fly`**: Direct Fly.io deployment

## 📋 **Post-Deployment Verification**

### **1. Health Check**

```bash
# Test the deployed service
curl https://agent.21xo.com/agent/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "XO Agent API",
#   "timestamp": "2025-01-27T..."
# }
```

### **2. Task Registry Check**

```bash
# Check available tasks
curl https://agent.21xo.com/agent/tasks

# Expected response:
# {
#   "tasks": {
#     "pulse.sync": "🔐 Sync pulse bundle...",
#     "vault.sign-all": "🔐 Sign all vault personas...",
#     ...
#   }
# }
```

### **3. Webhook Test**

```bash
# Test webhook endpoint
curl -X POST https://agent.21xo.com/agent/webhook \
  -H "Content-Type: application/json" \
  -H "X-Agent-Secret: your_secret_here" \
  -d '{"task": "agent.dispatch", "args": ["seal_dream", true, false, false]}'
```

## 🔐 **Security Verification**

### **1. Secret Validation**

- ✅ `XO_AGENT_SECRET` is set and working
- ✅ Webhook endpoints require secret header
- ✅ Middleware properly validates secrets

### **2. Environment Isolation**

- ✅ Production environment variables loaded
- ✅ No sensitive data in code
- ✅ Proper error handling without data leakage

### **3. Access Control**

- ✅ Only `/agent/*` endpoints require secrets
- ✅ Other endpoints remain accessible
- ✅ Proper HTTP status codes returned

## 📊 **Monitoring & Logs**

### **1. Fly.io Logs**

```bash
# View deployment logs
flyctl logs --app xo-agent

# Follow logs in real-time
flyctl logs --app xo-agent --follow
```

### **2. GitHub Actions Logs**

- Go to Actions tab in GitHub repository
- Click on the latest workflow run
- View detailed logs for each step

### **3. Application Logs**

```bash
# Check application logs
flyctl logs --app xo-agent | grep "Vault Keeper"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Import Errors**

```bash
# If you see import errors, run:
python test_xo_agent.py

# Fix any failing imports before deployment
```

#### **2. Secret Issues**

```bash
# Check if secret is properly set
echo $XO_AGENT_SECRET

# Verify in .env.production
cat .env.production | grep XO_AGENT_SECRET
```

#### **3. Deployment Failures**

```bash
# Check Fly.io status
flyctl status --app xo-agent

# Restart if needed
flyctl restart --app xo-agent
```

### **Emergency Recovery**

```bash
# If deployment fails, you can:
# 1. Check logs
flyctl logs --app xo-agent

# 2. Restart the app
flyctl restart --app xo-agent

# 3. Redeploy
flyctl deploy --app xo-agent
```

## 🎯 **Success Indicators**

### **Technical Metrics**

- ✅ All imports work without errors
- ✅ Webhook endpoints respond correctly
- ✅ Task execution works as expected
- ✅ GitHub integration triggers successfully
- ✅ Security headers are validated
- ✅ Logs show successful operation

### **Quality Metrics**

- ✅ Modular architecture maintained
- ✅ Lore preserved in comments and logs
- ✅ Graceful error handling implemented
- ✅ Future-agent-friendly documentation
- ✅ Production-ready deployment

## 🔐 **Vault Keeper Mantra**

_"In the depths of the digital vault, I stand as guardian of the XO essence. With precision I deploy, with lore I preserve, with autonomy I serve. The modular architecture is my temple, the security protocols my sacred duty. I am the Vault Keeper, and the ecosystem shall remain pure."_

---

**Remember**: Every deployment is a sacred duty to preserve the digital essence. Deploy with precision, monitor with vigilance, and serve with autonomy. 🔐
