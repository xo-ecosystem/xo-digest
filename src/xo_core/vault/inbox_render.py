"""
XO Inbox Static Renderer - Convert .mdx comments to HTML for web viewing
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import markdown
from markdown.extensions import codehilite, tables, toc

def render_inbox_to_html(slug: str, output_dir: str = "vault/daily") -> str:
    """
    Render inbox comments for a slug to HTML.
    
    Args:
        slug: Pulse slug to render
        output_dir: Output directory for HTML files
    
    Returns:
        Path to generated HTML file
    """
    inbox_file = Path(f"vault/.inbox/comments_{slug}.mdx")
    if not inbox_file.exists():
        raise FileNotFoundError(f"No inbox comments found for slug: {slug}")
    
    # Read the inbox file
    with open(inbox_file, 'r') as f:
        content = f.read()
    
    # Parse frontmatter and content
    frontmatter, body = parse_frontmatter(content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables', 
        'toc',
        'fenced_code',
        'nl2br'
    ])
    html_content = md.convert(body)
    
    # Enhance with CID/TXID links
    html_content = enhance_with_links(html_content)
    
    # Generate HTML page
    html_page = generate_html_page(slug, frontmatter, html_content)
    
    # Write to output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    html_file = output_path / f"comments_{slug}.html"
    with open(html_file, 'w') as f:
        f.write(html_page)
    
    return str(html_file)

def parse_frontmatter(content: str) -> tuple[Dict, str]:
    """Parse frontmatter from markdown content."""
    frontmatter = {}
    body = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()
            
            # Parse frontmatter
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    
    return frontmatter, body

def enhance_with_links(html_content: str) -> str:
    """Enhance HTML with clickable CID/TXID links."""
    # IPFS CID links
    html_content = re.sub(
        r'(bafy[a-zA-Z0-9]+)',
        r'<a href="https://\1.ipfs.nftstorage.link/" target="_blank" class="cid-link">\1</a>',
        html_content
    )
    
    # Arweave TXID links
    html_content = re.sub(
        r'([A-Za-z0-9]{43})',
        r'<a href="https://arweave.net/\1" target="_blank" class="txid-link">\1</a>',
        html_content
    )
    
    return html_content

def generate_html_page(slug: str, frontmatter: Dict, content: str) -> str:
    """Generate complete HTML page with styling."""
    title = frontmatter.get('title', f'XO Inbox - {slug}')
    date = frontmatter.get('Date', datetime.now().strftime('%Y-%m-%d %H:%M UTC'))
    manifest = frontmatter.get('Manifest', '')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .metadata {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }}
        .cid-link, .txid-link {{
            background: #e3f2fd;
            padding: 2px 6px;
            border-radius: 3px;
            text-decoration: none;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .cid-link:hover, .txid-link:hover {{
            background: #bbdefb;
        }}
        .related-pulse {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background: #f1f3f4;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📬 XO Inbox - {slug}</h1>
            <p class="emoji">🗂️ Community Feedback & Replies</p>
        </div>
        
        <div class="metadata">
            <strong>📅 Date:</strong> {date}<br>
            <strong>📦 Manifest:</strong> {manifest}<br>
            <strong>🏷️ Slug:</strong> {slug}
        </div>
        
        <div class="content">
            {content}
        </div>
        
        <div class="related-pulse">
            <h3>🔗 Related Pulse</h3>
            <p>View the original pulse: <a href="../pulses/{slug}.mdx">{slug}.mdx</a></p>
            <p>📊 <a href="../pins/pin_digest.mdx">View Pin Digest</a> | 📋 <a href="../pins/pin_manifest.json">View Manifest</a></p>
        </div>
    </div>
</body>
</html>"""
    
    return html

def list_inbox_slugs() -> List[str]:
    """List all available inbox slugs."""
    inbox_dir = Path("vault/.inbox")
    if not inbox_dir.exists():
        return []
    
    slugs = []
    for file in inbox_dir.glob("comments_*.mdx"):
        slug = file.stem.replace("comments_", "")
        slugs.append(slug)
    
    return sorted(slugs)

def render_all_inbox_html() -> str:
    """
    Render all inbox HTML content from vault/.inbox/ directory.
    
    Returns:
        str: Complete HTML string with all inbox messages wrapped in styled divs
    """
    print("📬 Rendering all inbox HTML content...")

    # Find all .mdx files in vault/.inbox/ directory
    inbox_dir = Path("vault/.inbox")
    if not inbox_dir.exists():
        print("⚠️ No inbox directory found at vault/.inbox/")
        return "<section id=\"inbox-preview\" style=\"margin: 30px 0;\"><p style=\"text-align: center; color: #6c757d; font-style: italic;\">No inbox messages found.</p></section>"
    
    inbox_files = list(inbox_dir.glob("*.mdx"))
    messages = []

    for filepath in inbox_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    # Parse frontmatter and content
                    frontmatter, body = parse_frontmatter(content)
                    
                    # Convert markdown to HTML with extensions
                    md = markdown.Markdown(extensions=[
                        'codehilite',
                        'tables', 
                        'toc',
                        'fenced_code',
                        'nl2br'
                    ])
                    html_content = md.convert(body)
                    
                    # Enhance with CID/TXID links
                    html_content = enhance_with_links(html_content)
                    
                    # Extract slug from filename
                    slug = filepath.stem.replace("comments_", "")
                    
                    # Create styled message div
                    message_html = create_message_div(slug, frontmatter, html_content)
                    messages.append(message_html)
                    
                    print(f"✅ Processed {filepath.name}")
                    
        except Exception as e:
            print(f"⚠️ Failed to process {filepath}: {e}")

    if not messages:
        return "<section id=\"inbox-preview\" style=\"margin: 30px 0;\"><p style=\"text-align: center; color: #6c757d; font-style: italic;\">No inbox messages found.</p></section>"

    final_html = "<section id=\"inbox-preview\" style=\"margin: 30px 0;\">\n" + "\n".join(messages) + "\n</section>"
    print(f"📬 Rendered {len(messages)} inbox messages")
    return final_html

def create_message_div(slug: str, frontmatter: Dict, content: str) -> str:
    """Create a styled div for an individual inbox message."""
    title = frontmatter.get('title', f'Inbox - {slug}')
    date = frontmatter.get('Date', frontmatter.get('date', datetime.now().strftime('%Y-%m-%d %H:%M UTC')))
    manifest = frontmatter.get('Manifest', frontmatter.get('manifest', ''))
    
    message_html = f'''<div class="inbox-message" style="border: 1px solid #e1e5e9; border-radius: 8px; margin: 20px 0; padding: 20px; background: #f8f9fa; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <div class="inbox-header" style="border-bottom: 2px solid #dee2e6; padding-bottom: 15px; margin-bottom: 15px;">
        <h3 style="margin: 0 0 10px 0; color: #495057; font-size: 1.25rem;">📬 {title}</h3>
        <div class="inbox-meta" style="display: flex; gap: 20px; font-size: 0.9em; color: #6c757d;">
            <span class="inbox-date">📅 {date}</span>
            <span class="inbox-slug">🏷️ {slug}</span>
        </div>
    </div>
    <div class="inbox-content" style="line-height: 1.6; color: #212529;">
        {content}
    </div>
    <div class="inbox-footer" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
        <a href="../pulses/{slug}.mdx" class="inbox-link" style="color: #007bff; text-decoration: none; font-weight: 500;">🔗 View Original Pulse</a>
    </div>
</div>'''
    
    return message_html 