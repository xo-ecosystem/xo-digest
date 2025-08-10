"""
XO Vault API Module - FastAPI-based backend for immutable, decentralized publishing

This module provides:
- FastAPI application for XO Vault API
- Pulse preview generator
- Inbox comment router
- Drop metadata server
- Signature dispatcher (using HashiCorp Vault secrets)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from pathlib import Path

# Import vault utilities
from .utils import vault_status, vault_pull_secrets
from .bootstrap import get_vault_client
from .signing import XOVaultSigner, sign_pulse, sign_drop, verify_signed_content

# FastAPI app initialization
app = FastAPI(
    title="XO Vault API",
    description="FastAPI-based backend for XO Vault immutable publishing",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class PulsePreview(BaseModel):
    slug: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class InboxComment(BaseModel):
    pulse_slug: str
    author: str
    content: str
    timestamp: Optional[str] = None


class DropMetadata(BaseModel):
    slug: str
    title: str
    description: Optional[str] = None
    assets: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class SignatureRequest(BaseModel):
    content_type: str  # "pulse", "drop", "comment"
    content_id: str
    content_hash: str
    requester: str

class AdvancedSignatureRequest(BaseModel):
    content: str
    content_type: str  # "pulse", "drop", "comment"
    algorithm: str = "ed25519"
    metadata: Optional[Dict[str, Any]] = None

class KeyManagementRequest(BaseModel):
    key_name: str
    algorithm: str = "ed25519"
    action: str  # "create", "rotate", "list", "export"


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for XO Vault API."""
    vault_healthy = vault_status()
    return {
        "status": "healthy",
        "vault_connected": vault_healthy,
        "version": "0.2.0",
        "architecture": "XO Vault System",
    }


# Pulse preview endpoint
@app.post("/pulse/preview")
async def generate_pulse_preview(pulse: PulsePreview):
    """Generate preview for a pulse."""
    try:
        # TODO: Implement actual preview generation
        preview_html = f"""
        <html>
        <head><title>Preview: {pulse.slug}</title></head>
        <body>
            <h1>Pulse Preview: {pulse.slug}</h1>
            <div class="content">{pulse.content}</div>
        </body>
        </html>
        """
        return {"slug": pulse.slug, "preview_html": preview_html, "status": "generated"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Preview generation failed: {str(e)}"
        )


# Inbox sync endpoint
@app.post("/inbox/sync")
async def sync_inbox_comment(comment: InboxComment):
    """Sync an inbox comment."""
    try:
        # TODO: Implement actual inbox sync
        return {
            "pulse_slug": comment.pulse_slug,
            "author": comment.author,
            "status": "synced",
            "timestamp": comment.timestamp or "now",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inbox sync failed: {str(e)}")


# Drop metadata endpoint
@app.post("/drop/metadata")
async def serve_drop_metadata(drop: DropMetadata):
    """Serve drop metadata."""
    try:
        # TODO: Implement actual metadata serving
        return {
            "slug": drop.slug,
            "title": drop.title,
            "description": drop.description,
            "assets": drop.assets,
            "status": "served",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Metadata serving failed: {str(e)}"
        )


# Advanced signature endpoint
@app.post("/vault/sign-advanced")
async def advanced_signature(request: AdvancedSignatureRequest):
    """Advanced cryptographic signing using HashiCorp Vault."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        # Create signer instance
        signer = XOVaultSigner(algorithm=request.algorithm)

        # Generate key name based on content type and timestamp
        from datetime import datetime
        key_name = f"{request.content_type}-signing-key-{datetime.now().strftime('%Y%m')}"

        # Ensure key exists
        try:
            signer.generate_key_pair(key_name, request.algorithm)
        except:
            # Key might already exist, continue
            pass

        # Sign the content
        signed_document = signer.sign_content(
            content=request.content,
            key_name=key_name,
            content_type=request.content_type,
            metadata=request.metadata
        )

        return {
            "status": "signed",
            "signed_document": signed_document,
            "algorithm": request.algorithm,
            "key_name": key_name
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Advanced signing failed: {str(e)}"
        )

# Legacy signature endpoint (for backward compatibility)
@app.post("/vault/sign")
async def dispatch_signature(request: SignatureRequest):
    """Legacy signature dispatch using HashiCorp Vault secrets."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        # Use advanced signing for legacy requests
        advanced_request = AdvancedSignatureRequest(
            content=f"legacy_content_{request.content_id}",
            content_type=request.content_type,
            algorithm="ed25519",
            metadata={"legacy_request": True, "requester": request.requester}
        )

        result = await advanced_signature(advanced_request)

        return {
            "content_type": request.content_type,
            "content_id": request.content_id,
            "signature": result["signed_document"]["signature"],
            "status": "signed",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Signature dispatch failed: {str(e)}"
        )


# Vault status endpoint
@app.get("/vault/status")
async def get_vault_status():
    """Get HashiCorp Vault status."""
    try:
        is_unsealed = vault_status()
        return {
            "vault_status": "unsealed" if is_unsealed else "sealed",
            "healthy": is_unsealed,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Vault status check failed: {str(e)}"
        )


# Key management endpoint
@app.post("/vault/keys")
async def manage_keys(request: KeyManagementRequest):
    """Manage signing keys in HashiCorp Vault."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        signer = XOVaultSigner(algorithm=request.algorithm)

        if request.action == "create":
            result = signer.generate_key_pair(request.key_name, request.algorithm)
            return {"status": "key_created", "result": result}

        elif request.action == "rotate":
            result = signer.rotate_key(request.key_name)
            return {"status": "key_rotated", "result": result}

        elif request.action == "list":
            keys = signer.list_keys()
            return {"status": "keys_listed", "keys": keys}

        elif request.action == "export":
            public_key = signer.export_public_key(request.key_name)
            return {"status": "key_exported", "public_key": public_key}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key management failed: {str(e)}")

# Signature verification endpoint
@app.post("/vault/verify")
async def verify_signature(signed_document: Dict[str, Any]):
    """Verify a cryptographic signature."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        result = verify_signed_content(signed_document)
        return {
            "status": "verified",
            "verification_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signature verification failed: {str(e)}")

# Pulse signing endpoint
@app.post("/vault/sign-pulse")
async def sign_pulse_endpoint(pulse_data: Dict[str, Any]):
    """Sign a pulse with advanced cryptographic signing."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        content = pulse_data.get("content", "")
        slug = pulse_data.get("slug", "")
        metadata = pulse_data.get("metadata", {})

        if not content or not slug:
            raise HTTPException(status_code=400, detail="Content and slug are required")

        signed_pulse = sign_pulse(content, slug, metadata)
        return {
            "status": "pulse_signed",
            "signed_pulse": signed_pulse
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pulse signing failed: {str(e)}")

# Drop signing endpoint
@app.post("/vault/sign-drop")
async def sign_drop_endpoint(drop_data: Dict[str, Any]):
    """Sign a drop with advanced cryptographic signing."""
    try:
        # Check if HashiCorp Vault is available
        client = get_vault_client()
        if client is None:
            raise HTTPException(status_code=503, detail="HashiCorp Vault not available")

        metadata = drop_data.get("metadata", {})
        slug = drop_data.get("slug", "")

        if not metadata or not slug:
            raise HTTPException(status_code=400, detail="Metadata and slug are required")

        signed_drop = sign_drop(metadata, slug)
        return {
            "status": "drop_signed",
            "signed_drop": signed_drop
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drop signing failed: {str(e)}")

# Secrets pull endpoint
@app.post("/vault/pull-secrets")
async def pull_vault_secrets():
    """Pull secrets from GitHub or local encrypted file."""
    try:
        vault_pull_secrets()
        return {"status": "secrets_pulled", "message": "Secrets pulled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Secrets pull failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8801)
