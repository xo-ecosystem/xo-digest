from fab_tasks.patch import apply_patch


def run_patch_hook(payload: dict) -> str:
    """
    Trigger patch tool using agent payload.
    Example payload:
    {
        "patch": {
            "pattern": ".*",
            "replacement": "New content"
        },
        "target": "content/pulses/eighth_seal_3d/drop.status.json"
    }
    """
    patch_data = payload.get("patch")
    target_path = payload.get("target")

    if not patch_data or not target_path:
        return "⚠️ Missing patch or target"

    result = apply_patch(target_path, [patch_data])
    return f"✅ Patch applied to {target_path}" if result else "❌ Patch failed"
