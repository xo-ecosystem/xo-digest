import os
from fastapi.templating import Jinja2Templates


# Templates live under ./templates (repo root by default). Override with XO_TEMPLATES_DIR
TEMPLATES_DIR = os.getenv("XO_TEMPLATES_DIR", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
