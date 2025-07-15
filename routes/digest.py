from fastapi import APIRouter
from xo_core.utils.digest_preview import render_all_digest_preview

router = APIRouter()

@router.get("/vault/daily/preview/all")
async def full_digest_preview():
    return render_all_digest_preview()
