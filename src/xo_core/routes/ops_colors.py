from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
from xo_core.routes.colors_stream import broadcast_colors_update


router = APIRouter(tags=["ops"])


# Path to the colors map served publicly
COLORS_FILE = os.path.join("public", "drops", "colors.json")
OPS_TOKEN = os.environ.get("OPS_TOKEN", "changeme")


def _check_token(token: str) -> None:
    if token != OPS_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")


class ColorsUpdate(BaseModel):
    mapping: dict


@router.get("/ops/colors")
def get_colors(token: str):
    _check_token(token)
    try:
        with open(COLORS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@router.post("/ops/colors")
def update_colors(payload: ColorsUpdate, token: str):
    _check_token(token)
    os.makedirs(os.path.dirname(COLORS_FILE), exist_ok=True)
    with open(COLORS_FILE, "w") as f:
        json.dump(payload.mapping, f, indent=2)
    broadcast_colors_update(payload.mapping)
    return {"ok": True, "mapping": payload.mapping}
