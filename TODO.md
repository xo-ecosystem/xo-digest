# ✅ XO Drop Patch – Cursor TODO Wrap (as of July 21)

## 🎯 GOAL

Prepare a clean, automated way to publish Drop metadata + assets from the Vault (drop.assets) into the public content tree (src/content/drops/<drop_id>), including support for shared meta, webp assets, and .drop.yml.

---

## 🛠️ FABRIC TASKS

1. ✅ **Fabric-enable drop_patch.py**

   - ✅ Wrapped patch_drop_yml() into a @task
   - ✅ Accept --drop=<id> argument
   - ✅ Register via ns = Collection("patch")

2. ✅ **Hook drop_patch into fabfile.py**

   - ✅ Use: ns.add_collection(drop_patch.ns, name="drop")
   - ✅ Ensure no .ns errors block xo-fab --list

3. ✅ **Fabric-enable drop_meta_sync.py**

   - ✅ Wrapped sync_meta() into a @task
   - ✅ Accept --drop=<id> argument with validation
   - ✅ Register via ns = Collection("drop_meta_sync")

4. ✅ **Hook drop_meta_sync into fabfile.py**
   - ✅ Use: ns.add_collection(drop_meta_sync_ns, name="meta")
   - ✅ Ensure no .ns errors block xo-fab --list

---

## 📂 FILE STRUCTURE & SYNC

3. ✅ **.drop.yml scaffolded**

   - ✅ Location: src/xo_core/vault/seals/eighth/drop.assets/.drop.yml
   - ✅ Includes:
     ```yaml
     drop: eighth
     title: Eighth Seal Drop
     image: webp/drop-symbol.webp
     variants:
       - scroll-teaser.webp
       - seal-flame.webp
       - darkmode-symbol.png
     ```

4. ✅ **drop.shared_meta.json added**

   - ✅ Path: src/xo_core/fab_tasks/drop.shared_meta.json
   - ✅ Used to inject dynamic title, description, tags

5. ✅ **drop_fallback_meta.py parses fallback**

   - ✅ Enhanced metadata generation with shared meta merging

6. ✅ **Sync .drop.yml + webp/\*.webp to src/content/drops/<drop_id>/**

   - ✅ Auto-create if missing
   - ✅ Copy without overwriting newer files (unless --force)
   - ✅ Support multiple asset types (webp, png, svg, jpg)

7. ✅ **Bundle metadata sync system**
   - ✅ drop.status.json per bundle with asset lists
   - ✅ drop.preview.yml per bundle with display config
   - ✅ Asset validation and file existence checks
   - ✅ Automatic drop.meta.json enhancement

---

## 🧪 TEST + VARIANT SUPPORT

7. ✅ **Test against:**

   - ✅ eighth (fully tested and working)
   - 🔄 (Optional) other drops like first, lolcats

8. ✅ **Support .coin.yml / .mdx / variant previews**
   - ✅ Bundle structure with metadata/drop.status.json
   - ✅ Asset tracking with ID, label, file references
   - ✅ Variant sync from webp/ folder contents
   - 🔄 Animate later if needed

---

## ✨ VISUALS + SYMBOLS

9. ✅ **drop-symbol.webp (25 KB)**
10. ✅ **drop-symbol.png (256 KB)**
11. ✅ **darkmode PNG variant (977 KB)**
12. 🔄 **Optional: drop-symbol.svg + animation loop**

---

## 🚀 AVAILABLE COMMANDS

### Drop Patch Commands:

```bash
# List available drops
xo-fab drop.patch --list

# Patch a specific drop
xo-fab drop.patch --drop=eighth

# Patch all drops
xo-fab drop.patch-all

# Validate all drops
xo-fab drop.validate

# Force overwrite existing files
xo-fab drop.patch --drop=eighth --force

# Only sync metadata, skip assets
xo-fab drop.patch --drop=eighth --meta-only
```

### Drop Meta Sync Commands:

```bash
# Sync meta for specific drop
xo-fab meta.sync --drop=eighth

# Sync all drops
xo-fab meta.sync-all

# Validate structure
xo-fab meta.validate --drop=eighth

# List available drops
xo-fab meta.sync --list

# Verbose output
xo-fab meta.sync --drop=eighth --verbose
```

---

## 📊 CURRENT STATUS

- ✅ **Fabric Task System**: Fully implemented and working
- ✅ **Asset Sync**: WebP, PNG, SVG, JPG support
- ✅ **Metadata Enhancement**: Shared meta merging
- ✅ **Validation**: Comprehensive drop validation
- ✅ **Bundle System**: Complete bundle metadata structure
- ✅ **Eighth Seal**: Fully patched and synced with bundle support
- ✅ **Meta Sync**: Automated drop.meta.json enhancement
- 🔄 **Frontend Integration**: Ready for React/Next.js integration
- 🔄 **Animation Support**: Framework ready for SVG animations

---

## 🧠 FOR CURSOR AGENT

Use this list to:

- ✅ Wire the drop_patch Fabric task (DONE)
- ✅ Validate and simplify the asset sync logic (DONE)
- ✅ Help patch the content tree and fabfile cleanly (DONE)
- ✅ Wire the drop_meta_sync Fabric task (DONE)
- ✅ Create bundle metadata structure (DONE)
- ✅ Implement automated meta enhancement (DONE)
- 🔄 Integrate with frontend components
- 🔄 Add animation support for SVG variants
- 🔄 Create additional drop templates (first, lolcats)

---

## 🎯 NEXT STEPS

1. **Frontend Integration**

   - Wire drop metadata into React components
   - Create dynamic drop preview pages
   - Add animation support for SVG symbols
   - Display bundle information and assets

2. **Additional Drops**

   - Create first seal drop structure
   - Add lolcats drop template
   - Test patch-all functionality
   - Implement bundle templates

3. **Advanced Features**

   - IPFS integration for asset storage
   - Blockchain metadata generation
   - Automated deployment triggers
   - Bundle-specific preview generation

4. **Cursor Agent Integration**
   - Use CURSOR_AGENT_PROMPT.md for automated operations
   - Implement bundle validation workflows
   - Create automated meta sync pipelines
   - Add intelligent asset management

---

## 📋 BUNDLE STRUCTURE EXAMPLE

```
src/xo_core/vault/seals/eighth/
├── seal_flame/
│   ├── metadata/
│   │   ├── drop.status.json    # Asset list and metadata
│   │   └── drop.preview.yml    # Display configuration
│   └── webp/
│       ├── seal_flame_core.webp
│       ├── flame_essence.webp
│       └── burning_seal.webp
└── drop.assets/
    ├── .drop.yml               # Drop configuration
    └── webp/                   # Main drop assets
```

---

**Status**: 🟢 **SYSTEM READY FOR PRODUCTION**

The XO Drop Patch and Meta Sync systems are fully functional and ready for the 21xo.exchange MVP sprint! 🚀

**New Features Added**:

- ✅ Bundle metadata system with drop.status.json
- ✅ Automated drop.meta.json enhancement
- ✅ Asset validation and file existence checks
- ✅ Cursor Agent prompt for automated operations
- ✅ Comprehensive validation and error reporting
