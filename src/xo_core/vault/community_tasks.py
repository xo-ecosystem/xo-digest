"""
XO Community Tasks - CLI tasks for community features
"""

from fabric import task
from pathlib import Path
import json
from datetime import datetime

@task
def inbox_render(ctx, slug=None, output_dir="vault/daily"):
    """Render inbox comments to HTML."""
    try:
        from .inbox_render import render_inbox_to_html, list_inbox_slugs
        
        if slug:
            # Render specific slug
            html_file = render_inbox_to_html(slug, output_dir)
            print(f"✅ Rendered inbox for {slug}: {html_file}")
        else:
            # Render all slugs
            slugs = list_inbox_slugs()
            if not slugs:
                print("⚠️ No inbox comments found")
                return
                
            for s in slugs:
                try:
                    html_file = render_inbox_to_html(s, output_dir)
                    print(f"✅ Rendered inbox for {s}: {html_file}")
                except Exception as e:
                    print(f"❌ Error rendering {s}: {e}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

@task
def agent_reply_suggest(ctx, slug=None, create_pulse=False):
    """Analyze inbox and suggest replies."""
    try:
        from .agent_reply import analyze_inbox_thread, suggest_reply_pulse, list_all_threads
        
        if slug:
            # Analyze specific thread
            analysis = analyze_inbox_thread(slug)
            if "error" in analysis:
                print(f"❌ {analysis['error']}")
                return
                
            print(f"📊 Analysis for {slug}:")
            print(f"  Mood: {analysis.get('mood', 'neutral')}")
            print(f"  Topics: {', '.join(analysis.get('topics', []))}")
            print(f"  Word Count: {analysis.get('word_count', 0)}")
            print(f"  Summary: {analysis.get('summary', 'No summary')}")
            
            print("\n💡 Suggestions:")
            for suggestion in analysis.get('suggestions', [])[:3]:
                print(f"  • {suggestion}")
                
            if create_pulse:
                pulse_data = suggest_reply_pulse(slug, analysis)
                pulse_file = Path(f"content/pulses/{pulse_data['slug']}.mdx")
                pulse_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(pulse_file, 'w') as f:
                    f.write(pulse_data['content'])
                    
                print(f"✅ Created reply pulse: {pulse_file}")
                
        else:
            # List all threads
            threads = list_all_threads()
            if not threads:
                print("⚠️ No inbox threads found")
                return
                
            print("📬 All Inbox Threads:")
            for thread in threads:
                if "error" in thread:
                    print(f"  ❌ {thread['slug']}: {thread['error']}")
                else:
                    print(f"  📝 {thread['slug']} ({thread.get('mood', 'neutral')}) - {thread.get('word_count', 0)} words")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

@task
def signal_broadcast(ctx, slug=None, channels="inbox", filters=None, health_check=False):
    """Broadcast social signals."""
    try:
        from .signal import SocialSignalBroadcaster
        
        broadcaster = SocialSignalBroadcaster()
        channel_list = channels.split(',') if channels else ['inbox']
        filter_list = filters.split(',') if filters else []
        
        if health_check:
            results = broadcaster.broadcast_health_check(channel_list)
        elif slug:
            results = broadcaster.broadcast_digest(slug, channel_list, filter_list)
        else:
            print("❌ Please specify --slug or --health-check")
            return
            
        print("📡 Broadcast Results:")
        for channel, result in results.items():
            if "error" in result:
                print(f"  ❌ {channel}: {result['error']}")
            else:
                print(f"  ✅ {channel}: {result.get('status', 'success')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

@task
def community_activate(ctx, slug=None, all_features=False):
    """Activate all community features for a slug."""
    try:
        print("🚀 Activating XO Community Features...")
        
        if slug:
            # Activate for specific slug
            print(f"\n📬 Rendering inbox for {slug}...")
            ctx.run(f"fab inbox.render --slug {slug}")
            
            print(f"\n🤖 Analyzing replies for {slug}...")
            ctx.run(f"fab agent.reply-suggest --slug {slug}")
            
            print(f"\n📡 Broadcasting signals for {slug}...")
            ctx.run(f"fab signal.broadcast --slug {slug} --channels inbox")
            
        elif all_features:
            # Activate for all slugs
            print("\n📬 Rendering all inboxes...")
            ctx.run("fab inbox.render")
            
            print("\n🤖 Analyzing all threads...")
            ctx.run("fab agent.reply-suggest")
            
            print("\n📡 Broadcasting health check...")
            ctx.run("fab signal.broadcast --health-check --channels inbox")
            
        else:
            print("❌ Please specify --slug or --all-features")
            return
            
        print("\n✅ Community features activated!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

@task
def community_status(ctx):
    """Show community system status."""
    try:
        print("🏥 XO Community System Status")
        print("=" * 40)
        
        # Check inbox files
        inbox_dir = Path("vault/.inbox")
        if inbox_dir.exists():
            inbox_files = list(inbox_dir.glob("comments_*.mdx"))
            print(f"📬 Inbox Comments: {len(inbox_files)}")
            for file in inbox_files[:5]:  # Show first 5
                slug = file.stem.replace("comments_", "")
                print(f"  • {slug}")
            if len(inbox_files) > 5:
                print(f"  ... and {len(inbox_files) - 5} more")
        else:
            print("📬 Inbox Comments: No inbox directory")
            
        # Check HTML renders
        daily_dir = Path("vault/daily")
        if daily_dir.exists():
            html_files = list(daily_dir.glob("comments_*.html"))
            print(f"🖼️ HTML Renders: {len(html_files)}")
        else:
            print("🖼️ HTML Renders: No daily directory")
            
        # Check pin digest
        digest_file = Path("vault/.pins/pin_digest.mdx")
        if digest_file.exists():
            print(f"📊 Pin Digest: Available")
        else:
            print(f"📊 Pin Digest: Not found")
            
        # Check manifest
        manifest_file = Path("vault/.pins/pin_manifest.json")
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            print(f"📋 Pin Manifest: {manifest.get('total_files', 0)} files")
        else:
            print(f"📋 Pin Manifest: Not found")
            
        print("\n🔧 Available Commands:")
        print("  fab inbox.render --slug <slug>")
        print("  fab agent.reply-suggest --slug <slug>")
        print("  fab signal.broadcast --slug <slug>")
        print("  fab community.activate --slug <slug>")
        
    except Exception as e:
        print(f"❌ Error: {e}") 