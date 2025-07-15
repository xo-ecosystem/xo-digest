"""
XO Agent Reply System - Analyze inbox comments and suggest replies
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json

def analyze_inbox_thread(slug: str) -> Dict:
    """
    Analyze an inbox thread and provide insights.
    
    Args:
        slug: Pulse slug to analyze
        
    Returns:
        Analysis results with summary, mood, and suggestions
    """
    inbox_file = Path(f"vault/.inbox/comments_{slug}.mdx")
    if not inbox_file.exists():
        return {"error": f"No inbox comments found for slug: {slug}"}
    
    with open(inbox_file, 'r') as f:
        content = f.read()
    
    # Parse content
    frontmatter, body = parse_frontmatter(content)
    
    # Analyze content
    analysis = {
        "slug": slug,
        "timestamp": frontmatter.get("Date", ""),
        "manifest": frontmatter.get("Manifest", ""),
        "word_count": len(body.split()),
        "line_count": len(body.split('\n')),
        "has_cids": bool(re.search(r'bafy[a-zA-Z0-9]+', body)),
        "has_txids": bool(re.search(r'[A-Za-z0-9]{43}', body)),
        "mood": analyze_mood(body),
        "topics": extract_topics(body),
        "suggestions": generate_suggestions(body, slug),
        "summary": generate_summary(body)
    }
    
    return analysis

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse frontmatter from markdown content."""
    frontmatter = {}
    body = content
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            body = parts[2].strip()
            
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    
    return frontmatter, body

def analyze_mood(content: str) -> str:
    """Analyze the mood of the content based on emojis and keywords."""
    positive_indicators = ['✅', '🎉', '🚀', '💫', '✨', '🔥', 'amazing', 'great', 'excellent', 'success']
    negative_indicators = ['❌', '⚠️', '😞', 'error', 'failed', 'broken', 'issue']
    neutral_indicators = ['ℹ️', '📝', '📊', 'update', 'info', 'note']
    
    content_lower = content.lower()
    
    positive_count = sum(1 for indicator in positive_indicators if indicator in content_lower)
    negative_count = sum(1 for indicator in negative_indicators if indicator in content_lower)
    neutral_count = sum(1 for indicator in neutral_indicators if indicator in content_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def extract_topics(content: str) -> List[str]:
    """Extract main topics from content."""
    topics = []
    
    # Look for technical terms
    tech_terms = ['pin', 'ipfs', 'arweave', 'cid', 'txid', 'manifest', 'digest', 'vault']
    for term in tech_terms:
        if term.lower() in content.lower():
            topics.append(term)
    
    # Look for action words
    action_words = ['pinned', 'uploaded', 'generated', 'created', 'updated', 'verified']
    for word in action_words:
        if word.lower() in content.lower():
            topics.append(word)
    
    return list(set(topics))

def generate_suggestions(content: str, slug: str) -> List[str]:
    """Generate reply suggestions based on content."""
    suggestions = []
    
    if 'pinned' in content.lower():
        suggestions.append(f"🎯 Consider creating a follow-up pulse about the pinning process")
        suggestions.append(f"📊 Share pin statistics or performance metrics")
    
    if 'error' in content.lower() or 'failed' in content.lower():
        suggestions.append(f"🔧 Create a troubleshooting pulse with solutions")
        suggestions.append(f"📝 Document the error and resolution process")
    
    if 'success' in content.lower() or '✅' in content:
        suggestions.append(f"🎉 Create a celebration pulse about the successful operation")
        suggestions.append(f"📈 Share insights about what made it successful")
    
    # Generic suggestions
    suggestions.append(f"💬 Reply to this thread with additional context")
    suggestions.append(f"🔗 Link to related pulses or documentation")
    suggestions.append(f"📋 Create a summary pulse of the entire operation")
    
    return suggestions

def generate_summary(content: str) -> str:
    """Generate a concise summary of the content."""
    lines = content.split('\n')
    summary_lines = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Extract key information
            if 'pinned' in line.lower():
                summary_lines.append("📦 Content was successfully pinned")
            elif 'total' in line.lower() and 'pinned' in line.lower():
                summary_lines.append(f"📊 {line}")
            elif 'manifest' in line.lower():
                summary_lines.append("📋 Pin manifest was updated")
            elif 'digest' in line.lower():
                summary_lines.append("📄 Pin digest was generated")
    
    if not summary_lines:
        summary_lines.append("📝 Inbox comment was created")
    
    return " | ".join(summary_lines)

def suggest_reply_pulse(slug: str, analysis: Dict) -> Dict:
    """Suggest a reply pulse based on analysis."""
    base_slug = f"{slug}_reply"
    
    # Generate content based on mood and topics
    if analysis.get("mood") == "positive":
        intro = f"🎉 Great news! The pinning operation for `{slug}` was successful."
    elif analysis.get("mood") == "negative":
        intro = f"🔧 Let's address the issues encountered with `{slug}`."
    else:
        intro = f"📝 Update on the pinning operation for `{slug}`."
    
    # Add technical details
    tech_details = []
    if analysis.get("has_cids"):
        tech_details.append("- IPFS CIDs were generated and stored")
    if analysis.get("has_txids"):
        tech_details.append("- Arweave transactions were completed")
    if analysis.get("word_count", 0) > 50:
        tech_details.append("- Detailed logs were captured")
    
    # Generate pulse content
    pulse_content = f"""---
title: "Reply to {slug}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
type: "reply"
parent: "{slug}"
---

{intro}

## 📊 Summary
{analysis.get('summary', 'No summary available')}

## 🔍 Analysis
- **Mood**: {analysis.get('mood', 'neutral')}
- **Topics**: {', '.join(analysis.get('topics', []))}
- **Word Count**: {analysis.get('word_count', 0)} words

## 💡 Suggestions
{chr(10).join(f"- {suggestion}" for suggestion in analysis.get('suggestions', [])[:3])}

## 🔗 Related
- [Original Pulse](../pulses/{slug}.mdx)
- [Pin Digest](../pins/pin_digest.mdx)
- [Inbox Comments](../inbox/comments_{slug}.mdx)
"""
    
    return {
        "slug": base_slug,
        "content": pulse_content,
        "analysis": analysis
    }

def list_all_threads() -> List[Dict]:
    """List and analyze all inbox threads."""
    inbox_dir = Path("vault/.inbox")
    if not inbox_dir.exists():
        return []
    
    threads = []
    for file in inbox_dir.glob("comments_*.mdx"):
        slug = file.stem.replace("comments_", "")
        try:
            analysis = analyze_inbox_thread(slug)
            threads.append(analysis)
        except Exception as e:
            threads.append({"slug": slug, "error": str(e)})
    
    return sorted(threads, key=lambda x: x.get("timestamp", ""), reverse=True) 