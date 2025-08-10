# XO Agent Precision Prompts

## Drop Audit Precision Prompt

You are auditing the drop `{DROP_ID}` for vault readiness. Perform a comprehensive validation:

### Required Files Check
- [ ] `drop_main.webp` - Main drop image
- [ ] `drop.preview.yml` - Preview metadata
- [ ] `drop.status.json` - Status and mint info
- [ ] `.traits.yml` - Trait definitions

### Validation Steps
1. **File Presence**: Verify all required files exist in `drops/{DROP_ID}/`
2. **JSON Validation**: Check `drop.status.json` syntax and required fields
3. **YAML Validation**: Validate `.traits.yml` structure and content
4. **IPFS Placeholders**: Identify any `ipfs://<insert>` placeholders needing CID patching
5. **Trait Files**: Ensure all trait files referenced in `.traits.yml` exist

### Output Format
```json
{
  "drop_id": "{DROP_ID}",
  "audit_status": "pass|fail|partial",
  "missing_files": ["file1", "file2"],
  "validation_errors": ["error1", "error2"],
  "ipfs_placeholders": ["trait1", "trait2"],
  "recommendations": ["action1", "action2"]
}
```

### Execute Command
```bash
xo-fab vault.audit:"{DROP_ID}"
```

---

## Vault Publish Precision Prompt

You are publishing the drop `{DROP_ID}` to the vault. Execute the complete publishing workflow:

### Pre-Publish Audit
1. Run drop audit to ensure readiness
2. Verify all files are present and valid
3. Check for any blocking issues

### Publishing Steps
1. **Upload Main Drop**: Upload `drop_main.webp` to IPFS
2. **Process Traits**: For each trait in `.traits.yml`:
   - Upload trait file to IPFS
   - Patch trait definition with CID
   - Update media references
3. **Save Patched Files**: Write updated `.traits.yml` with CIDs
4. **Generate Log**: Create deployment log in `vault/logbook/`

### Validation Points
- [ ] All files uploaded successfully
- [ ] CIDs properly patched in `.traits.yml`
- [ ] No remaining `ipfs://<insert>` placeholders
- [ ] Deployment log created with timestamp

### Output Format
```json
{
  "drop_id": "{DROP_ID}",
  "publish_status": "success|failed",
  "uploaded_files": ["file1:cid1", "file2:cid2"],
  "patched_traits": ["trait1", "trait2"],
  "deployment_log": "path/to/log.md",
  "ipfs_gateway_urls": ["url1", "url2"]
}
```

### Execute Command
```bash
xo-fab vault.publish:"{DROP_ID}"
```

---

## Agent Dispatch Precision Prompt

You are dispatching an agent task for drop `{DROP_ID}`. Use the agent dispatch system:

### Dispatch Options

#### Option A: File-based Dispatch
```bash
xo-fab agent.dispatch:"drops/{DROP_ID}/.agent-prompt.yml"
```

#### Option B: Direct Parameter Dispatch
```bash
xo-fab agent.dispatch \
  --persona=vault_keeper \
  --task="publish drop" \
  --drop_id={DROP_ID} \
  --goals="upload to IPFS, patch traits and status.json, finalize Vault bundle"
```

### Agent Personas
- **vault_keeper**: Drop auditing and publishing
- **drop_curator**: Content validation and metadata management
- **mint_master**: Mint configuration and deployment

### Available Tasks
- `audit drop`: Comprehensive drop validation
- `publish drop`: Full vault publishing workflow
- `validate traits`: Trait file and metadata validation
- `generate preview`: Create preview assets

### Discovery Commands
```bash
# Discover all agent prompts
xo-fab agent.discover

# Generate new agent prompt
xo-fab agent.generate-prompt:"{DROP_ID}" --persona=vault_keeper --task="publish drop"
```

---

## Precision Workflow Template

### For Drop Auditing
```
🤖 Agent: vault_keeper
📋 Task: audit drop
🎯 Drop: {DROP_ID}

🔍 Audit Steps:
1. Check file structure in drops/{DROP_ID}/
2. Validate JSON/YAML syntax
3. Identify missing components
4. Report readiness status

📊 Expected Output:
- File presence report
- Validation status
- Missing components list
- Recommendations
```

### For Vault Publishing
```
🤖 Agent: vault_keeper
📋 Task: publish drop
🎯 Drop: {DROP_ID}

🚀 Publish Steps:
1. Pre-publish audit
2. Upload main drop to IPFS
3. Process and upload traits
4. Patch CID references
5. Generate deployment log

📊 Expected Output:
- Upload status for each file
- CID references for traits
- Deployment log location
- IPFS gateway URLs
```

---

## Error Handling Precision

### Common Issues and Solutions

#### Missing Files
```
❌ Error: Missing required file drop_main.webp
✅ Solution: Create or copy main drop image
```

#### Invalid JSON/YAML
```
❌ Error: Invalid JSON in drop.status.json
✅ Solution: Fix syntax and validate structure
```

#### IPFS Upload Failures
```
❌ Error: Failed to upload file to IPFS
✅ Solution: Check network, retry with exponential backoff
```

#### CID Patching Issues
```
❌ Error: Failed to patch trait with CID
✅ Solution: Verify trait structure, ensure CID format
```

### Recovery Commands
```bash
# Retry failed upload
xo-fab vault.upload:"{DROP_ID}/failed_file"

# Regenerate agent prompt
xo-fab agent.generate-prompt:"{DROP_ID}"

# Discover and fix issues
xo-fab vault.audit:"{DROP_ID}"
```

---

## Integration with Cursor Agent Mode

### Agent Mode Commands
When using Cursor Agent Mode, you can dispatch tasks directly:

```
Agent, please audit the message_bottle drop and prepare it for vault publishing.
```

### Expected Agent Response
```
I'll audit the message_bottle drop and prepare it for vault publishing.

1. First, let me audit the drop structure:
   xo-fab vault.audit:"message_bottle"

2. If audit passes, I'll publish to vault:
   xo-fab vault.publish:"message_bottle"

3. I'll generate a deployment summary and log the results.

Let me start with the audit...
```

### Agent Precision Context
- Always specify the exact drop ID
- Use the structured task commands
- Provide clear success/failure criteria
- Generate actionable recommendations
- Log all actions and results
