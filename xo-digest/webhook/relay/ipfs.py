

import json
import os
import aiohttp
from pathlib import Path

async def upload_to_ipfs(file_path: Path, *, api_url: str, api_key: str = None):
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist")

    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=file_path.name)

            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            async with session.post(api_url, data=data, headers=headers) as resp:
                resp.raise_for_status()
                result = await resp.json()

                cid = result.get("cid") or result.get("Hash")
                if not cid:
                    raise ValueError("CID not found in response")

                # Format IPFS return data for Vault linking
                return {
                    "cid": cid,
                    "ipfs_uri": f"ipfs://{cid}",
                    "gateway_url": f"https://ipfs.io/ipfs/{cid}",
                    "markdown_embed": f"[IPFS File](https://ipfs.io/ipfs/{cid})"
                }

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/api/ipfs-upload")
async def ipfs_upload(
    file: UploadFile = File(...),
    api_url: str = Form(...),
    api_key: str = Form(None)
):
    try:
        # Save temp file
        temp_path = Path(f"/tmp/{file.filename}")
        with open(temp_path, "wb") as buffer:
            buffer.write(await file.read())

        result = await upload_to_ipfs(temp_path, api_url=api_url, api_key=api_key)

        # Optionally delete temp file after use
        temp_path.unlink(missing_ok=True)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))