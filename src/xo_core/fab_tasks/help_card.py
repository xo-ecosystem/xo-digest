from invoke import task, Collection

@task
def help_card(c):
    """
    🖼️ Print the XO-Fab CLI cheatsheet (PNG/SVG) to the terminal.
    """
    import os
    from pathlib import Path

    # Try to print SVG/PNG from a known location
    cheatsheet_svg = Path("docs/cli_cheatsheet.svg")
    cheatsheet_png = Path("docs/cli_cheatsheet.png")

    if cheatsheet_svg.exists():
        print("\n🖼️ XO-Fab CLI Cheatsheet (SVG):\n")
        print(cheatsheet_svg.read_text())
        return
    elif cheatsheet_png.exists():
        print("\n🖼️ XO-Fab CLI Cheatsheet (PNG path):\n")
        print(f"[Open this file in your browser or image viewer:] {cheatsheet_png.resolve()}")
        return
    else:
        print("❌ No cheatsheet SVG or PNG found in docs/. Please add cli_cheatsheet.svg or cli_cheatsheet.png.")

# Register namespace
ns = Collection("help_card")
ns.add_task(help_card) 