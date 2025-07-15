from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from pathlib import Path
import yaml

def render_mdx_preview(mdx_path: Path, persona_avatar: str = "", persona_name: str = ""):
    # Read the MDX content
    content = mdx_path.read_text(encoding="utf-8")

    # Load persona metadata if available
    metadata_path = mdx_path.parent / f"{mdx_path.stem}.yml"
    if metadata_path.exists():
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        persona_avatar = metadata.get("avatar", persona_avatar)
        persona_name = metadata.get("name", persona_name)

    # Prepare the avatar and name HTML only if provided
    avatar_html = f'<img src="{persona_avatar}" alt="{persona_name} avatar">' if persona_avatar else ""
    name_html = f'<h2>{persona_name}</h2>' if persona_name else ""

    # Render the preview HTML with optional avatar and name
    html = f"""
    <div class="preview">
        {avatar_html}
        {name_html}
        <div class="content">
            {content}
        </div>
    </div>
    """
    return html


# FastAPI route for inbox preview
@app.get("/inbox/preview/{persona}", response_class=HTMLResponse)
def preview_inbox(persona: str):
    path = Path(f"vault/.inbox/comments_{persona}.mdx")
    if not path.exists():
        return HTMLResponse(content=f"❌ No reply found for: {persona}", status_code=404)
    # Load metadata if available
    metadata_path = path.with_suffix(".yml")
    persona_avatar = ""
    persona_name = ""
    if metadata_path.exists():
        metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        persona_avatar = metadata.get("avatar", "")
        persona_name = metadata.get("name", "")

    return render_mdx_preview(path, persona_avatar=persona_avatar, persona_name=persona_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)