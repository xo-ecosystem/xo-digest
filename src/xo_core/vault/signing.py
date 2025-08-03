"""
XO Vault Advanced Signing Module - Cryptographic operations for immutable publishing

This module provides:
- Cryptographic signing using HashiCorp Vault
- Key management and rotation
- Signature verification
- Content hashing and integrity checks
- Multi-algorithm support (Ed25519, RSA, ECDSA)
"""

import hashlib
import json
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import os

# Import vault utilities
from .bootstrap import get_vault_client
from .utils import log_status

# Supported signing algorithms
SUPPORTED_ALGORITHMS = {
    "ed25519": "Ed25519 digital signature",
    "rsa": "RSA digital signature",
    "ecdsa": "ECDSA digital signature",
    "sha256": "SHA-256 hash verification"
}

class XOVaultSigner:
    """Advanced signing class for XO Vault cryptographic operations."""
    
    def __init__(self, algorithm: str = "ed25519"):
        self.algorithm = algorithm.lower()
        if self.algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        self.client = get_vault_client()
        if self.client is None:
            raise RuntimeError("HashiCorp Vault client not available")
    
    def generate_key_pair(self, key_name: str, key_type: str = None) -> Dict[str, str]:
        """Generate a new key pair in HashiCorp Vault."""
        if key_type is None:
            key_type = self.algorithm
        
        try:
            # Create key in Vault's transit engine
            key_config = {
                "type": key_type,
                "exportable": False,
                "allow_plaintext_backup": False
            }
            
            # Use Vault's transit engine to create the key
            response = self.client.secrets.transit.create_or_update_key(
                name=key_name,
                mount_point="transit",
                **key_config
            )
            
            if response.status_code == 204:
                log_status(f"Generated {key_type} key pair: {key_name}", "info")
                return {
                    "key_name": key_name,
                    "algorithm": key_type,
                    "status": "created",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                raise Exception(f"Failed to create key: {response.text}")
                
        except Exception as e:
            log_status(f"Key generation failed: {e}", "error")
            raise
    
    def sign_content(self, content: Union[str, bytes], key_name: str, 
                    content_type: str = "pulse", metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Sign content using HashiCorp Vault."""
        try:
            # Prepare content for signing
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = content
            
            # Create content hash
            content_hash = hashlib.sha256(content_bytes).hexdigest()
            
            # Prepare signing context
            signing_context = {
                "content_type": content_type,
                "content_hash": content_hash,
                "algorithm": self.algorithm,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata or {}
            }
            
            # Convert context to bytes for signing
            context_bytes = json.dumps(signing_context, sort_keys=True).encode('utf-8')
            
            # Sign using Vault's transit engine
            response = self.client.secrets.transit.sign_data(
                name=key_name,
                mount_point="transit",
                hash_algorithm="sha2-256",
                input_data=base64.b64encode(context_bytes).decode('utf-8')
            )
            
            if response.status_code == 200:
                signature_data = response.json()["data"]
                signature = signature_data["signature"]
                
                # Create signed document
                signed_document = {
                    "content": content if isinstance(content, str) else content.decode('utf-8'),
                    "content_type": content_type,
                    "content_hash": content_hash,
                    "signature": signature,
                    "algorithm": self.algorithm,
                    "key_name": key_name,
                    "timestamp": signing_context["timestamp"],
                    "metadata": metadata or {},
                    "vault_version": "0.2.0"
                }
                
                log_status(f"Content signed successfully: {content_type}", "info")
                return signed_document
            else:
                raise Exception(f"Signing failed: {response.text}")
                
        except Exception as e:
            log_status(f"Content signing failed: {e}", "error")
            raise
    
    def verify_signature(self, signed_document: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signature using HashiCorp Vault."""
        try:
            # Extract signature and context
            signature = signed_document["signature"]
            content_hash = signed_document["content_hash"]
            key_name = signed_document["key_name"]
            algorithm = signed_document.get("algorithm", self.algorithm)
            
            # Recreate signing context
            signing_context = {
                "content_type": signed_document["content_type"],
                "content_hash": content_hash,
                "algorithm": algorithm,
                "timestamp": signed_document["timestamp"],
                "metadata": signed_document.get("metadata", {})
            }
            
            context_bytes = json.dumps(signing_context, sort_keys=True).encode('utf-8')
            
            # Verify signature using Vault's transit engine
            response = self.client.secrets.transit.verify_signed_data(
                name=key_name,
                mount_point="transit",
                hash_algorithm="sha2-256",
                input_data=base64.b64encode(context_bytes).decode('utf-8'),
                signature=signature
            )
            
            if response.status_code == 200:
                verification_data = response.json()["data"]
                is_valid = verification_data["valid"]
                
                result = {
                    "valid": is_valid,
                    "content_hash": content_hash,
                    "key_name": key_name,
                    "algorithm": algorithm,
                    "timestamp": signed_document["timestamp"],
                    "verification_timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                log_status(f"Signature verification: {'VALID' if is_valid else 'INVALID'}", 
                          "info" if is_valid else "error")
                return result
            else:
                raise Exception(f"Verification failed: {response.text}")
                
        except Exception as e:
            log_status(f"Signature verification failed: {e}", "error")
            raise
    
    def list_keys(self) -> List[Dict[str, str]]:
        """List all available signing keys."""
        try:
            response = self.client.secrets.transit.list_keys(mount_point="transit")
            
            if response.status_code == 200:
                keys_data = response.json()["data"]["keys"]
                keys = []
                
                for key_name in keys_data:
                    # Get key details
                    key_response = self.client.secrets.transit.read_key(
                        name=key_name,
                        mount_point="transit"
                    )
                    
                    if key_response.status_code == 200:
                        key_info = key_response.json()["data"]
                        keys.append({
                            "name": key_name,
                            "type": key_info.get("type", "unknown"),
                            "creation_time": key_info.get("creation_time", 0),
                            "deletion_allowed": key_info.get("deletion_allowed", False)
                        })
                
                return keys
            else:
                raise Exception(f"Failed to list keys: {response.text}")
                
        except Exception as e:
            log_status(f"Key listing failed: {e}", "error")
            raise
    
    def rotate_key(self, key_name: str) -> Dict[str, str]:
        """Rotate a signing key."""
        try:
            response = self.client.secrets.transit.rotate_key(
                name=key_name,
                mount_point="transit"
            )
            
            if response.status_code == 204:
                log_status(f"Key rotated successfully: {key_name}", "info")
                return {
                    "key_name": key_name,
                    "status": "rotated",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                raise Exception(f"Key rotation failed: {response.text}")
                
        except Exception as e:
            log_status(f"Key rotation failed: {e}", "error")
            raise
    
    def export_public_key(self, key_name: str) -> str:
        """Export public key for verification."""
        try:
            response = self.client.secrets.transit.read_key(
                name=key_name,
                mount_point="transit"
            )
            
            if response.status_code == 200:
                key_data = response.json()["data"]
                public_key = key_data.get("keys", {}).get("1", {}).get("public_key", "")
                
                if public_key:
                    log_status(f"Public key exported: {key_name}", "info")
                    return public_key
                else:
                    raise Exception("Public key not available")
            else:
                raise Exception(f"Failed to export public key: {response.text}")
                
        except Exception as e:
            log_status(f"Public key export failed: {e}", "error")
            raise

def sign_pulse(pulse_content: str, pulse_slug: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """Sign a pulse with advanced cryptographic signing."""
    try:
        signer = XOVaultSigner(algorithm="ed25519")
        key_name = f"pulse-signing-key-{datetime.now().strftime('%Y%m')}"
        
        # Ensure key exists
        try:
            signer.generate_key_pair(key_name)
        except:
            # Key might already exist, continue
            pass
        
        # Sign the pulse
        signed_pulse = signer.sign_content(
            content=pulse_content,
            key_name=key_name,
            content_type="pulse",
            metadata={
                "slug": pulse_slug,
                "signing_purpose": "pulse_publication",
                **(metadata or {})
            }
        )
        
        return signed_pulse
        
    except Exception as e:
        log_status(f"Pulse signing failed: {e}", "error")
        raise

def sign_drop(drop_metadata: Dict[str, Any], drop_slug: str) -> Dict[str, Any]:
    """Sign a drop with advanced cryptographic signing."""
    try:
        signer = XOVaultSigner(algorithm="ed25519")
        key_name = f"drop-signing-key-{datetime.now().strftime('%Y%m')}"
        
        # Ensure key exists
        try:
            signer.generate_key_pair(key_name)
        except:
            # Key might already exist, continue
            pass
        
        # Convert metadata to string for signing
        metadata_str = json.dumps(drop_metadata, sort_keys=True)
        
        # Sign the drop
        signed_drop = signer.sign_content(
            content=metadata_str,
            key_name=key_name,
            content_type="drop",
            metadata={
                "slug": drop_slug,
                "signing_purpose": "drop_publication"
            }
        )
        
        return signed_drop
        
    except Exception as e:
        log_status(f"Drop signing failed: {e}", "error")
        raise

def verify_signed_content(signed_document: Dict[str, Any]) -> Dict[str, Any]:
    """Verify any signed content."""
    try:
        signer = XOVaultSigner(algorithm=signed_document.get("algorithm", "ed25519"))
        return signer.verify_signature(signed_document)
        
    except Exception as e:
        log_status(f"Content verification failed: {e}", "error")
        raise 