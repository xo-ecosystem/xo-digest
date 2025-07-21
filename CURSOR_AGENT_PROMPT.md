# 🧠 XO Drop Meta Sync Agent Prompt

# Use inside src/content/drops/<drop> in Cursor

## 🎯 TASK:

Ensure this drop folder is fully structured and synced across:

- drop.meta.json (global metadata)
- drop.status.json files per bundle (inside drop.assets/<drop>/...)
- drop.preview.yml files per bundle

## ✅ GOALS:

### 1. Validate and patch drop.meta.json:

- Title
- Bundle list (e.g. ["seal_flame", "eighth_seal_3d", "message_bottle"])
- Variants (match filenames in `webp/`)
- Description, tags, category, rarity, minting, launch_date
- Social links

### 2. Scan all bundles:

For each in drop.assets/<drop>/\*/metadata:

- Load drop.status.json
- Extract asset list (id, label, file)
- Check asset files exist
- Append missing entries to drop.meta.json

### 3. Normalize:

- All file references should use lowercase kebab-case `.webp`
- All bundles should include matching drop.status.json
- Sync asset filenames with `webp/` folder when possible

### 4. If drop.meta.json exists:

- Patch in missing fields only (don't overwrite author edits)
- Use comments to mark incomplete fields

### 5. Commit as: "🔁 Synced drop.meta.json with bundle asset metadata"

## 🔧 EXAMPLE FILE STRUCTURE:

```
- src/content/drops/eighth/drop.meta.json
- drop.assets/eighth/seal_flame/metadata/drop.status.json
- drop.assets/eighth/seal_flame/webp/*.webp
```

## 💡 Tips:

- Drop is named by folder (e.g. "eighth")
- Bundle = subfolder in drop.assets/<drop>/
- Asset ID = drop*<row>*<col> or unique slug
- Add error comments if assets are missing

---

## 🎯 XO DROP STRUCTURE CHECK (Agent Prompt)

Given a drop folder at `src/content/drops/<drop>`:

### 1. Validate drop.meta.json schema

Check for required fields:

```json
{
  "drop": "string",
  "title": "string",
  "description": "string",
  "image": "string",
  "variants": ["array"],
  "bundles": ["array"],
  "assets": ["array"],
  "tags": ["array"],
  "category": "string",
  "rarity": "string",
  "mint_price": "string",
  "max_supply": "number",
  "launch_date": "string",
  "status": "string",
  "social_links": "object"
}
```

### 2. Load bundles from drop.assets/<drop>/ and scan:

- `metadata/drop.status.json`
- `metadata/drop.preview.yml`

### 3. Extract asset list (id, label, file)

From each drop.status.json:

```json
{
  "assets": [
    {
      "id": "eighth_0_0",
      "label": "Seal Flame Core",
      "file": "seal_flame_core.webp"
    }
  ]
}
```

### 4. Update drop.meta.json:

- Add missing "bundles" field
- Sync variant references (if any)
- Align preview image references
- Annotate any missing asset files

### 5. Warn if inconsistencies are found between bundles and meta

### 6. Auto-commit changes with clear commit message

---

## 🛠️ Available Commands:

### Fabric Tasks (if available):

```bash
# Sync meta for specific drop
xo-fab meta.sync --drop=eighth

# Sync all drops
xo-fab meta.sync-all

# Validate structure
xo-fab meta.validate --drop=eighth

# List available drops
xo-fab meta.sync --list
```

### Manual Process:

1. **Scan Structure**: Check all bundle directories
2. **Load Metadata**: Read drop.status.json files
3. **Validate Assets**: Ensure webp files exist
4. **Update Meta**: Patch drop.meta.json with findings
5. **Commit Changes**: Use descriptive commit message

---

## 🔍 Validation Checklist:

- [ ] drop.meta.json exists and is valid JSON
- [ ] All bundles listed in drop.meta.json exist in vault
- [ ] Each bundle has metadata/drop.status.json
- [ ] All asset files referenced in drop.status.json exist
- [ ] Variants list matches actual webp files
- [ ] Asset IDs follow naming convention (drop_row_col)
- [ ] No duplicate asset IDs across bundles
- [ ] All required metadata fields are present

---

## 🚨 Error Handling:

### Missing Files:

- Add warning comments in drop.meta.json
- Create placeholder drop.status.json if missing
- Log missing asset files for manual review

### Inconsistent Data:

- Flag mismatched asset IDs
- Warn about missing bundle metadata
- Suggest corrections for file naming

### Invalid Structure:

- Report malformed JSON/YAML
- Identify missing required fields
- Provide fix suggestions

---

## 📝 Commit Message Template:

```
🔁 Synced drop.meta.json with bundle asset metadata

- Updated bundles list: [bundle1, bundle2, ...]
- Added assets: [asset1, asset2, ...]
- Fixed variants: [variant1, variant2, ...]
- Patched missing fields: [field1, field2, ...]
- Warnings: [warning1, warning2, ...]

Drop: {drop_id}
Bundles: {bundle_count}
Assets: {asset_count}
Status: {validation_status}
```

---

## 🎯 Success Criteria:

✅ **drop.meta.json** contains all bundle references
✅ **All assets** from drop.status.json are listed
✅ **Variants** match actual webp files
✅ **No missing files** warnings
✅ **Consistent naming** across all references
✅ **Valid JSON structure** with all required fields

---

**Ready to execute drop meta sync operations! 🚀**
