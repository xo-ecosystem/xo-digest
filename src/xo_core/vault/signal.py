"""
XO Social Signal Layer - Broadcast digest and pin summaries to social channels
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import os

class SocialSignalBroadcaster:
    """Broadcast XO Vault signals to social channels."""
    
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
    def broadcast_digest(self, slug: str, channels: List[str] = None, filters: List[str] = None) -> Dict:
        """
        Broadcast pin digest to social channels.
        
        Args:
            slug: Pulse slug
            channels: List of channels to broadcast to
            filters: Optional filters (infra, drops, replies)
            
        Returns:
            Results of broadcast attempts
        """
        if channels is None:
            channels = ['inbox']
        if filters is None:
            filters = []
            
        # Load digest content
        digest_file = Path("vault/.pins/pin_digest.mdx")
        if not digest_file.exists():
            return {"error": "No pin digest found"}
            
        with open(digest_file, 'r') as f:
            digest_content = f.read()
            
        # Load manifest for metadata
        manifest_file = Path("vault/.pins/pin_manifest.json")
        manifest = {}
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                
        # Create broadcast message
        message = self._format_broadcast_message(slug, digest_content, manifest, filters)
        
        results = {}
        
        # Broadcast to each channel
        for channel in channels:
            try:
                if channel == 'discord' and self.discord_webhook:
                    results['discord'] = self._send_to_discord(message)
                elif channel == 'telegram' and self.telegram_bot_token:
                    results['telegram'] = self._send_to_telegram(message)
                elif channel == 'inbox':
                    results['inbox'] = self._send_to_inbox(message, slug)
                else:
                    results[channel] = {"error": f"Channel {channel} not configured"}
            except Exception as e:
                results[channel] = {"error": str(e)}
                
        return results
    
    def _format_broadcast_message(self, slug: str, digest_content: str, manifest: Dict, filters: List[str]) -> str:
        """Format message for social broadcast."""
        # Extract key stats from manifest
        total_files = manifest.get('total_files', 0)
        total_size = manifest.get('total_size', 0)
        ipfs_pins = manifest.get('ipfs_pins', 0)
        arweave_pins = manifest.get('arweave_pins', 0)
        
        # Format size
        size_mb = total_size / (1024 * 1024) if total_size > 0 else 0
        
        # Create message
        message = f"""🚀 **XO Vault Pin Summary - {slug}**

📊 **Stats:**
• Files Pinned: {total_files}
• Total Size: {size_mb:.2f} MB
• IPFS Pins: {ipfs_pins}
• Arweave Pins: {arweave_pins}

📅 **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

🔗 **Links:**
• [Pin Digest](https://github.com/xo/xo-core/blob/main/vault/.pins/pin_digest.mdx)
• [Pin Manifest](https://github.com/xo/xo-core/blob/main/vault/.pins/pin_manifest.json)
• [Original Pulse](https://github.com/xo/xo-core/blob/main/content/pulses/{slug}.mdx)

"""
        
        # Add filters if specified
        if filters:
            message += f"🏷️ **Tags:** {', '.join(f'#{filter}' for filter in filters)}\n\n"
            
        # Add digest preview (first 200 chars)
        digest_preview = digest_content[:200] + "..." if len(digest_content) > 200 else digest_content
        message += f"📝 **Preview:**\n{digest_preview}"
        
        return message
    
    def _send_to_discord(self, message: str) -> Dict:
        """Send message to Discord webhook."""
        payload = {
            "content": message,
            "username": "XO Vault Bot",
            "avatar_url": "https://github.com/xo/xo-core/raw/main/public/logo.png"
        }
        
        response = requests.post(self.discord_webhook, json=payload)
        return {
            "status": response.status_code,
            "response": response.text if response.status_code != 204 else "Success"
        }
    
    def _send_to_telegram(self, message: str) -> Dict:
        """Send message to Telegram bot."""
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload)
        return {
            "status": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
    
    def _send_to_inbox(self, message: str, slug: str) -> Dict:
        """Send message to XO Inbox."""
        try:
            from .inbox import send_to_xo_inbox
            
            # Create a social signal comment
            social_comment = f"""---
title: "Social Signal - {slug}"
Date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
Type: "social_signal"
Channel: "broadcast"
---

{message}

---
*Auto-generated by XO Social Signal Layer*
"""
            
            # Send to inbox
            result = send_to_xo_inbox(social_comment, "vault/.pins/pin_manifest.json", f"{slug}_social")
            
            return {
                "status": "success",
                "file": result
            }
        except Exception as e:
            return {"error": str(e)}
    
    def broadcast_health_check(self, channels: List[str] = None) -> Dict:
        """Broadcast vault health status."""
        if channels is None:
            channels = ['inbox']
            
        # Check vault health
        health_status = self._check_vault_health()
        
        message = f"""🏥 **XO Vault Health Check**

📊 **Status:** {health_status['status']}
📁 **Total Files:** {health_status['total_files']}
📦 **Pinned Files:** {health_status['pinned_files']}
🔗 **IPFS CIDs:** {health_status['ipfs_cids']}
🌐 **Arweave TXs:** {health_status['arweave_txs']}

📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

"""
        
        if health_status['issues']:
            message += f"⚠️ **Issues:**\n{chr(10).join(f'• {issue}' for issue in health_status['issues'])}\n"
            
        results = {}
        for channel in channels:
            try:
                if channel == 'discord' and self.discord_webhook:
                    results['discord'] = self._send_to_discord(message)
                elif channel == 'telegram' and self.telegram_bot_token:
                    results['telegram'] = self._send_to_telegram(message)
                elif channel == 'inbox':
                    results['inbox'] = self._send_to_inbox(message, "health_check")
            except Exception as e:
                results[channel] = {"error": str(e)}
                
        return results
    
    def _check_vault_health(self) -> Dict:
        """Check vault health status."""
        vault_dir = Path("vault")
        pins_dir = vault_dir / ".pins"
        signed_dir = vault_dir / ".signed"
        synced_dir = vault_dir / ".synced"
        
        health = {
            "status": "healthy",
            "total_files": 0,
            "pinned_files": 0,
            "ipfs_cids": 0,
            "arweave_txs": 0,
            "issues": []
        }
        
        # Count files
        if vault_dir.exists():
            for file in vault_dir.rglob("*"):
                if file.is_file() and not file.name.startswith('.'):
                    health["total_files"] += 1
                    
                    # Check if pinned
                    if file.suffix in ['.ipfs_cid', '.arweave_tx']:
                        health["pinned_files"] += 1
                        if file.suffix == '.ipfs_cid':
                            health["ipfs_cids"] += 1
                        elif file.suffix == '.arweave_tx':
                            health["arweave_txs"] += 1
        
        # Check for issues
        if not pins_dir.exists():
            health["issues"].append("Pins directory missing")
            health["status"] = "warning"
            
        if not signed_dir.exists():
            health["issues"].append("Signed directory missing")
            health["status"] = "warning"
            
        if health["pinned_files"] == 0 and health["total_files"] > 0:
            health["issues"].append("No files pinned")
            health["status"] = "warning"
            
        return health 