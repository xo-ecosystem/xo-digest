@router.post("/webhook/sanity")
async def sanity_webhook(request: Request):
    try:
        payload = await request.json()
        content_type = payload.get("_type", "unknown")
        content_title = payload.get("title", "untitled")
        slug = payload.get("slug", {}).get("current", "unnamed")

        if "body" in payload:
            body_content = payload["body"]
            md_text = f"# {content_title}\n\n{body_content}"
            filename = f"{slug}.mdx"
            cid = await upload_to_ipfs(md_text.encode("utf-8"), filename=filename)

            # Write .ipfs.mdx stub
            stub_path = f"vault/.signed/{slug}.ipfs.mdx"
            os.makedirs(os.path.dirname(stub_path), exist_ok=True)
            with open(stub_path, "w") as stub:
                stub.write(f"---\ncid: {cid}\ntitle: \"{content_title}\"\nslug: {slug}\n---\n\n")
                stub.write(md_text)

            # Trigger .ipfs.sync (optional chaining)
            try:
                from xo_core.fab_tasks.pulse.ipfs_sync import ipfs_sync
                ipfs_sync(slug=slug)
            except ImportError:
                pass  # Placeholder: IPFS sync not yet wired

            # Optional: Add Vault preview logic here
            # Vault preview rendering (optional)
            from xo_core.utils.markdown_renderer import render_markdown_to_html
            preview_html = render_markdown_to_html(md_text)

            preview_path = f"vault/.preview/{slug}.html"
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            with open(preview_path, "w") as f:
                f.write(preview_html)

            # Copy preview to /vault/daily/{slug}.preview.html for Vault Explorer rendering
            daily_preview_path = f"vault/daily/{slug}.preview.html"
            os.makedirs(os.path.dirname(daily_preview_path), exist_ok=True)
            with open(daily_preview_path, "w") as daily_file:
                daily_file.write(preview_html)

            # Trigger GitHub Pages or Arweave sync
            try:
                from xo_core.fab_tasks.vault.explorer_auto import (
                    sync_preview_to_explorer,
                    push_to_arweave,
                    upload_to_github_pages,
                )
                sync_preview_to_explorer(slug)
                push_to_arweave(f"vault/daily/{slug}.preview.html")
                upload_to_github_pages(f"vault/daily/{slug}.preview.html")
            except ImportError:
                pass  # Optional sync functions not wired yet

            return JSONResponse({
                "status": "ok",
                "message": "Uploaded to IPFS",
                "cid": cid,
                "stub": stub_path
            })

        raise HTTPException(status_code=400, detail="Missing 'body' field in payload")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))