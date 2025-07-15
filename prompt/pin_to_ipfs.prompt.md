# Codex: pin_to_ipfs

## Overview
This function uploads a file to IPFS using the active backend (Pinata, nft.storage, or local IPFS daemon).
It reads the backend from `IPFS_PROVIDER` environment variable, and API tokens from `.env`.

## Use Cases
- Auto-pin Vault assets during signing/archiving
- Return CID links for content verification
- Log operations and fallback gracefully on errors
- Support multiple IPFS providers for redundancy

## Function Signature
```python
def pin_to_ipfs(file_path: Union[str, Path], provider: Optional[str] = None) -> str:
```

## Parameters
- `file_path`: Path to the file to pin (string or Path object)
- `provider`: Override the IPFS_PROVIDER environment variable (optional)

## Returns
- IPFS URI in format: `ipfs://<cid>`

## Environment Configuration
```bash
# Choose your IPFS provider
IPFS_PROVIDER=nftstorage  # or: pinata, local

# For Pinata
PINATA_API_KEY=your_pinata_jwt_token

# For nft.storage  
NFT_STORAGE_TOKEN=your_nft_storage_api_token
```

## Backend Support

### 1. nft.storage (Default)
- **API**: https://api.nft.storage/upload
- **Token**: `NFT_STORAGE_TOKEN`
- **Response**: `{"value": {"cid": "bafy..."}}`
- **Gateway**: `https://{cid}.ipfs.nftstorage.link/`

### 2. Pinata
- **API**: https://api.pinata.cloud/pinning/pinFileToIPFS
- **Token**: `PINATA_API_KEY` (JWT)
- **Response**: `{"IpfsHash": "Qm..."}`
- **Gateway**: `https://gateway.pinata.cloud/ipfs/{cid}`

### 3. Local IPFS Daemon
- **Command**: `ipfs add -Q <file>`
- **Requires**: IPFS CLI installed (`brew install ipfs`)
- **Gateway**: Local daemon gateway

## Error Handling
- **FileNotFoundError**: File doesn't exist
- **IPFSBackendError**: Backend-specific errors (API failures, missing tokens)
- **Graceful fallback**: Logs errors but doesn't crash the application

## Examples

### Basic Usage
```python
from xo_core.vault.ipfs_utils import pin_to_ipfs

# Pin a file using default provider
cid = pin_to_ipfs("vault/signed/pulse.mdx")
print(cid)  # ipfs://bafyFakeCID123...
```

### With Provider Override
```python
# Force use of Pinata
cid = pin_to_ipfs("vault/signed/pulse.mdx", provider="pinata")
```

### Error Handling
```python
try:
    cid = pin_to_ipfs("nonexistent.mdx")
except FileNotFoundError:
    print("File not found")
except IPFSBackendError as e:
    print(f"IPFS error: {e}")
```

## Integration with Fabric Tasks

### Auto-pin on Sign
```python
@task
def sign_pulse(c, slug):
    # ... signing logic ...
    signed_file = f"vault/signed/{slug}.mdx"
    
    # Auto-pin to IPFS
    try:
        cid = pin_to_ipfs(signed_file)
        print(f"✅ Pinned to IPFS: {cid}")
    except IPFSBackendError as e:
        print(f"⚠️ IPFS pinning failed: {e}")
```

### Test IPFS Connection
```python
from xo_core.vault.ipfs_utils import test_ipfs_connection

result = test_ipfs_connection()
print(f"Provider: {result['provider']}")
print(f"Status: {result['status']}")
print(f"Config: {result['config']}")
```

## Testing
Run the comprehensive test suite:
```bash
python -m pytest tests/test_ipfs_utils.py -v
```

## Codex/Agent0 Integration
- **Type hints**: Full typing support for IDE assistance
- **Docstrings**: Comprehensive documentation for AI assistance
- **Error handling**: Clear error messages for debugging
- **Configuration**: Environment-based configuration for flexibility

## Common Issues

### Missing API Token
```
IPFSBackendError: PINATA_API_KEY not configured
```
**Solution**: Add your API token to `.env` file

### IPFS CLI Not Found
```
IPFSBackendError: IPFS CLI not found. Install with: brew install ipfs
```
**Solution**: Install IPFS CLI or switch to cloud provider

### API Rate Limits
```
IPFSBackendError: Pinata API error: 429 - Rate limit exceeded
```
**Solution**: Wait and retry, or switch to different provider

## Best Practices
1. **Always handle exceptions** when calling `pin_to_ipfs()`
2. **Use environment variables** for configuration
3. **Test your setup** with `test_ipfs_connection()`
4. **Log operations** for debugging and monitoring
5. **Have fallback providers** configured for redundancy 