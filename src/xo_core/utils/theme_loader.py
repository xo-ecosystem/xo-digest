from pathlib import Path
import markdown

# TODO: Consider replacing this injection with a shared `theme_loader.get_html_template()` utility in the future.

def get_html_template() -> str:
    """Extracts the HTML preview template embedded in the Tailwind config comment block."""
    tailwind_config_path = Path(__file__).parent / 'tailwind.config.js'
    if not tailwind_config_path.exists():
        return ""

    tailwind_text = tailwind_config_path.read_text(encoding='utf-8')
    start_marker = '/**'
    end_marker = '*/'
    start_index = tailwind_text.find(start_marker)
    end_index = tailwind_text.find(end_marker, start_index + len(start_marker))
    if start_index == -1 or end_index == -1:
        return ""

    comment_block = tailwind_text[start_index + len(start_marker):end_index].strip()
    lines = comment_block.splitlines()
    cleaned_lines = [line.lstrip(' *') for line in lines]
    return '\n'.join(cleaned_lines)


def generate_html_from_markdown(md_path: Path, output_path: Path):
    # Read the markdown content
    md_content = md_path.read_text(encoding='utf-8')

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'toc'])

    template_html = get_html_template() or f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>XO Pulse Preview</title>
</head>
<body>
{html_content}
</body>
</html>"""

    if template_html != "" and '<!-- Your MDX-rendered HTML content here -->' in template_html:
        # Replace the placeholder with actual rendered HTML content
        placeholder = '<!-- Your MDX-rendered HTML content here -->'
        template_html = template_html.replace(placeholder, html_content)
    elif template_html != "":
        # If placeholder not found, append the content inside the body tag
        import re
        body_match = re.search(r'<body[^>]*>', template_html)
        if body_match:
            insert_pos = body_match.end()
            template_html = template_html[:insert_pos] + '\n' + html_content + template_html[insert_pos:]
        else:
            # No body tag found, just append at the end
            template_html += '\n' + html_content

    # Write the final HTML to output_path
    output_path.write_text(template_html, encoding='utf-8')