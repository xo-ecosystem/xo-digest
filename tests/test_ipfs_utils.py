"""
Unit tests for IPFS utilities.

Tests cover multi-backend support, error handling, and configuration validation.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import os

from xo_core.vault.ipfs_utils import (
    pin_to_ipfs, 
    test_ipfs_connection, 
    get_ipfs_gateway_url,
    IPFSBackendError
)


class TestIPFSPin(unittest.TestCase):
    """Test IPFS pinning functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_file = Path("testfile.txt")
        self.test_content = b"Hello, IPFS!"
    
    def tearDown(self):
        """Clean up test files."""
        if self.test_file.exists():
            self.test_file.unlink()
    
    @patch('xo_core.vault.ipfs_utils.requests.post')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'pinata', 'PINATA_API_KEY': 'test_key'})
    def test_pin_to_ipfs_pinata(self, mock_post):
        """Test pinning to Pinata backend."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"IpfsHash": "QmFakeCID123"}
        mock_post.return_value = mock_response
        
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        result = pin_to_ipfs(self.test_file)
        
        self.assertEqual(result, "ipfs://QmFakeCID123")
        mock_post.assert_called_once()
    
    @patch('xo_core.vault.ipfs_utils.requests.post')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'nftstorage', 'NFT_STORAGE_TOKEN': 'test_token'})
    def test_pin_to_ipfs_nftstorage(self, mock_post):
        """Test pinning to nft.storage backend."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": {"cid": "bafyFakeCID456"}}
        mock_post.return_value = mock_response
        
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        result = pin_to_ipfs(self.test_file)
        
        self.assertEqual(result, "ipfs://bafyFakeCID456")
        mock_post.assert_called_once()
    
    @patch('subprocess.run')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'local'})
    def test_pin_to_ipfs_local(self, mock_run):
        """Test pinning to local IPFS daemon."""
        # Mock successful subprocess
        mock_result = MagicMock()
        mock_result.stdout = "QmLocalCID789\n"
        mock_run.return_value = mock_result
        
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        result = pin_to_ipfs(self.test_file)
        
        self.assertEqual(result, "ipfs://QmLocalCID789")
        mock_run.assert_called_once()
    
    def test_pin_to_ipfs_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(FileNotFoundError):
            pin_to_ipfs("nonexistent_file.txt")
    
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'pinata'}, clear=True)
    def test_pin_to_ipfs_missing_api_key(self):
        """Test error handling for missing API key."""
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        with self.assertRaises(IPFSBackendError) as cm:
            pin_to_ipfs(self.test_file)
        
        self.assertIn("PINATA_API_KEY not configured", str(cm.exception))
    
    @patch('xo_core.vault.ipfs_utils.requests.post')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'pinata', 'PINATA_API_KEY': 'test_key'})
    def test_pin_to_ipfs_api_error(self, mock_post):
        """Test error handling for API failures."""
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        with self.assertRaises(IPFSBackendError) as cm:
            pin_to_ipfs(self.test_file)
        
        self.assertIn("Pinata API error: 401", str(cm.exception))
    
    def test_pin_to_ipfs_unsupported_provider(self):
        """Test error handling for unsupported providers."""
        # Create test file
        with open(self.test_file, "wb") as f:
            f.write(self.test_content)
        
        with self.assertRaises(IPFSBackendError) as cm:
            pin_to_ipfs(self.test_file, provider="unsupported")
        
        self.assertIn("Unsupported IPFS provider", str(cm.exception))


class TestIPFSConnection(unittest.TestCase):
    """Test IPFS connection and configuration validation."""
    
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'pinata', 'PINATA_API_KEY': 'test_key'})
    def test_test_ipfs_connection_pinata_configured(self):
        """Test connection test with configured Pinata."""
        result = test_ipfs_connection()
        
        self.assertEqual(result["provider"], "pinata")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["config"]["api_key"], "configured")
    
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'pinata'}, clear=True)
    def test_test_ipfs_connection_pinata_missing(self):
        """Test connection test with missing Pinata config."""
        result = test_ipfs_connection()
        
        self.assertEqual(result["provider"], "pinata")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["config"]["api_key"], "missing")
    
    @patch('subprocess.run')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'local'})
    def test_test_ipfs_connection_local_available(self, mock_run):
        """Test connection test with available local IPFS."""
        mock_run.return_value = MagicMock()
        
        result = test_ipfs_connection()
        
        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["config"]["ipfs_cli"], "available")
    
    @patch('subprocess.run')
    @patch.dict(os.environ, {'IPFS_PROVIDER': 'local'})
    def test_test_ipfs_connection_local_missing(self, mock_run):
        """Test connection test with missing local IPFS."""
        mock_run.side_effect = FileNotFoundError()
        
        result = test_ipfs_connection()
        
        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["status"], "error")


class TestIPFSGateway(unittest.TestCase):
    """Test IPFS gateway URL generation."""
    
    def test_get_ipfs_gateway_url_nftstorage(self):
        """Test nft.storage gateway URL generation."""
        cid = "QmTestCID123"
        url = get_ipfs_gateway_url(cid, "nftstorage")
        expected = "https://QmTestCID123.ipfs.nftstorage.link/"
        self.assertEqual(url, expected)
    
    def test_get_ipfs_gateway_url_ipfs_io(self):
        """Test ipfs.io gateway URL generation."""
        cid = "QmTestCID123"
        url = get_ipfs_gateway_url(cid, "ipfs.io")
        expected = "https://ipfs.io/ipfs/QmTestCID123"
        self.assertEqual(url, expected)
    
    def test_get_ipfs_gateway_url_cloudflare(self):
        """Test Cloudflare gateway URL generation."""
        cid = "QmTestCID123"
        url = get_ipfs_gateway_url(cid, "cloudflare")
        expected = "https://cloudflare-ipfs.com/ipfs/QmTestCID123"
        self.assertEqual(url, expected)
    
    def test_get_ipfs_gateway_url_default(self):
        """Test default gateway URL generation."""
        cid = "QmTestCID123"
        url = get_ipfs_gateway_url(cid, "unknown")
        expected = "https://QmTestCID123.ipfs.nftstorage.link/"
        self.assertEqual(url, expected)


if __name__ == '__main__':
    unittest.main() 