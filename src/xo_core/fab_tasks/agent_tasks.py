"""
XO Core Agent Tasks
AI-powered exploration, cosmic prompting, and creative generation
"""

from invoke import task, Collection
import json
import yaml
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import hashlib


@task
def cosmic(c, drop_id, variant="scroll_01", persona="vault_keeper"):
    """Generate cosmic prompt using AI agent for creative workflows"""
    print(f"🌌 Generating cosmic prompt for {drop_id}:{variant} with {persona}")

    script_path = Path("scripts/cosmic_agent_wrapper.py")
    if not script_path.exists():
        print(f"❌ Cosmic agent script not found: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), drop_id, variant, persona],
            capture_output=True,
            text=True,
            check=True,
        )

        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Cosmic agent failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


@task
def explore(c, drop_id, model="gpt-4.5"):
    """
    Agent-assisted drop explorer: reads traits, lore, inbox, suggests new content.
    Integrates with GPT-4.5/GPT-5 for enhanced creative suggestions.
    """
    print(f"🧠 Exploring drop '{drop_id}' with {model}")

    # Locate drop directory
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id,
    ]

    drop_path = None
    for path in drop_paths:
        if path.exists():
            drop_path = path
            break

    if not drop_path:
        print(f"❌ Drop not found: {drop_id}")
        return False

    print(f"📁 Found drop at: {drop_path}")

    # Load existing metadata
    metadata = {}

    # Load status
    status_file = drop_path / f"{drop_id}.status.json"
    if status_file.exists():
        with open(status_file) as f:
            metadata["status"] = json.load(f)
            print(f"✅ Loaded status: {metadata['status'].get('title', drop_id)}")

    # Load traits
    traits_file = drop_path / "hidden" / ".traits.yml"
    if traits_file.exists():
        with open(traits_file) as f:
            metadata["traits"] = yaml.safe_load(f)
            print(f"🧩 Loaded {len(metadata['traits'])} traits")
    else:
        print("💡 No traits file found - creating directory")
        (drop_path / "hidden").mkdir(exist_ok=True)

    # Load existing lore
    lore_file = drop_path / ".lore.yml"
    if lore_file.exists():
        with open(lore_file) as f:
            metadata["lore"] = yaml.safe_load(f)
            print(f"📜 Loaded existing lore")

    # Generate suggestions using cosmic agent
    print(f"\n🎨 Generating creative suggestions...")

    # Run cosmic agent for suggestions
    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/cosmic_agent_wrapper.py",
                drop_id,
                "exploration",
                "lore_weaver",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("🌌 Cosmic Agent Output:")
        print("=" * 40)
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Cosmic agent failed, continuing with basic exploration: {e}")

    # Create/update lore file with exploration timestamp
    exploration_data = {
        "explored_at": datetime.now().isoformat(),
        "model_used": model,
        "suggestions": {
            "narrative_threads": [
                "Connection to other drops in the vault",
                "Hidden backstory elements",
                "Evolution pathway possibilities",
            ],
            "trait_expansions": [
                "Game compatibility enhancements",
                "Cross-universe trait bridges",
                "Community interaction hooks",
            ],
        },
        "next_steps": [
            "Develop trait variants",
            "Create inbox engagement prompts",
            "Design cross-drop connections",
        ],
    }

    # Merge with existing lore
    if "lore" in metadata:
        exploration_data = {**metadata["lore"], **exploration_data}

    # Write updated lore file
    with open(lore_file, "w") as f:
        yaml.dump(exploration_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Updated lore file: {lore_file}")

    # Generate inbox seed
    inbox_dir = drop_path / "inbox"
    inbox_dir.mkdir(exist_ok=True)

    seed_file = inbox_dir / "seed.mdx"
    if not seed_file.exists():
        seed_content = f"""# 📬 {metadata.get('status', {}).get('title', drop_id)} - Community Inbox

Welcome to the conversation around this drop!

## 🎯 What's This About?

{metadata.get('status', {}).get('description', 'A unique drop in the XO universe with hidden depths waiting to be explored.')}

## 💭 Join the Conversation

- What story do you see in this drop?
- How might it connect to other parts of the XO universe?
- What questions would you ask the creator?

## 🧩 Traits & Lore

*Discover the hidden characteristics and backstory elements that make this drop unique.*

---

*Generated by XO Agent Explorer - {datetime.now().isoformat()}*
*No ownership required - all perspectives welcome!*
"""

        with open(seed_file, "w") as f:
            f.write(seed_content)

        print(f"✅ Created inbox seed: {seed_file}")

    print(f"\n🎉 Exploration complete for: {drop_id}")
    return True


@task
def explore_drop(c, drop="message_bottle", model="gpt-4.5"):
    """
    Agent-assisted drop explorer: reads traits, lore, inbox, suggests new content.
    """
    print(f"🧠 Exploring drop '{drop}' with {model}")

    # Locate drop directory
    drop_paths = [
        Path("drops") / drop,
        Path("drops/drafts") / drop,
        Path("drops/sealed") / drop,
        Path("vault/drops") / drop,
    ]

    drop_path = None
    for path in drop_paths:
        if path.exists():
            drop_path = path
            break

    if not drop_path:
        print(f"❌ Drop not found: {drop}")
        return False

    print(f"📁 Found drop at: {drop_path}")

    # Load existing metadata
    metadata = {}

    # Load status
    status_file = drop_path / f"{drop}.status.json"
    if status_file.exists():
        with open(status_file) as f:
            metadata["status"] = json.load(f)
            print(f"✅ Loaded status: {metadata['status'].get('title', drop)}")

    # Load traits
    traits_file = drop_path / "hidden" / ".traits.yml"
    if traits_file.exists():
        with open(traits_file) as f:
            metadata["traits"] = yaml.safe_load(f)
            print(f"🧩 Loaded {len(metadata['traits'])} traits")
    else:
        print("💡 No traits file found - creating directory")
        (drop_path / "hidden").mkdir(exist_ok=True)

    # Load existing lore
    lore_file = drop_path / ".lore.yml"
    if lore_file.exists():
        with open(lore_file) as f:
            metadata["lore"] = yaml.safe_load(f)
            print(f"📜 Loaded existing lore")

    # Generate suggestions using cosmic agent
    print(f"\n🎨 Generating creative suggestions...")

    # Run cosmic agent for suggestions
    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/cosmic_agent_wrapper.py",
                drop,
                "exploration",
                "lore_weaver",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("🌌 Cosmic Agent Output:")
        print("=" * 40)
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Cosmic agent failed, continuing with basic exploration: {e}")

    # Create/update lore file with exploration timestamp
    exploration_data = {
        "explored_at": datetime.now().isoformat(),
        "model_used": model,
        "suggestions": {
            "narrative_threads": [
                "Connection to other drops in the vault",
                "Hidden backstory elements",
                "Evolution pathway possibilities",
            ],
            "trait_expansions": [
                "Game compatibility enhancements",
                "Cross-universe trait bridges",
                "Community interaction hooks",
            ],
        },
        "next_steps": [
            "Develop trait variants",
            "Create inbox engagement prompts",
            "Design cross-drop connections",
        ],
    }

    # Merge with existing lore
    if "lore" in metadata:
        exploration_data = {**metadata["lore"], **exploration_data}

    # Write updated lore file
    with open(lore_file, "w") as f:
        yaml.dump(exploration_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Updated lore file: {lore_file}")

    # Generate inbox seed
    inbox_dir = drop_path / "inbox"
    inbox_dir.mkdir(exist_ok=True)

    seed_file = inbox_dir / "seed.mdx"
    if not seed_file.exists():
        seed_content = f"""# 📬 {metadata.get('status', {}).get('title', drop)} - Community Inbox

Welcome to the conversation around this drop!

## 🎯 What's This About?

{metadata.get('status', {}).get('description', 'A unique drop in the XO universe with hidden depths waiting to be explored.')}

## 💭 Join the Conversation

- What story do you see in this drop?
- How might it connect to other parts of the XO universe?
- What questions would you ask the creator?

## 🧩 Traits & Lore

*Discover the hidden characteristics and backstory elements that make this drop unique.*

---

*Generated by XO Agent Explorer - {datetime.now().isoformat()}*
*No ownership required - all perspectives welcome!*
"""

        with open(seed_file, "w") as f:
            f.write(seed_content)

        print(f"✅ Created inbox seed: {seed_file}")

    print(f"\n🎉 Exploration complete for: {drop}")
    return True


@task
def dispatch(c, persona="vault_keeper", prompt=None, drop_id=None):
    """
    CLI task to dispatch a persona with optional webhook, preview, and memory support.
    Enhanced for GPT-4.5/GPT-5 integration.
    """
    print(f"🤖 Dispatching {persona} agent")

    if not prompt and not drop_id:
        print("❌ Either --prompt or --drop-id required")
        return False

    # If drop_id provided, generate context from drop
    if drop_id:
        print(f"📦 Loading context from drop: {drop_id}")
        cosmic_prompt = subprocess.run(
            [
                sys.executable,
                "scripts/cosmic_agent_wrapper.py",
                drop_id,
                "exploration",
                persona,
            ],
            capture_output=True,
            text=True,
        )

        if cosmic_prompt.returncode == 0:
            context = cosmic_prompt.stdout
        else:
            context = f"Drop context for {drop_id} (failed to load details)"
    else:
        context = prompt

    # Enhanced dispatch logic would integrate with your AI service here
    print(f"🧠 Context loaded ({len(context)} chars)")
    print(f"🎭 Persona: {persona}")

    if drop_id:
        print(f"📦 Drop: {drop_id}")

    print("\n" + "=" * 50)
    print("COSMIC CONTEXT:")
    print("=" * 50)
    print(context)

    # TODO: Integrate with actual AI service (OpenAI GPT-4.5, local model, etc.)
    # For now, display the enhanced context

    print("\n✅ Agent dispatch completed")
    return True


@task
def trait_bridge(c, drop_id, action="create", game=None):
    """
    Manage trait bridges for external game compatibility.

    Args:
        drop_id: The drop ID to work with
        action: 'create' to create bridges, 'export' to export for a game
        game: Game name for export (mario_kart, sims, minecraft)
    """
    print(f"🌉 Managing trait bridges for: {drop_id}")

    if action == "create":
        print("🔨 Creating trait bridges...")
        try:
            from xo_core.trait_bridge import create_bridge_from_traits

            success = create_bridge_from_traits(drop_id)
            if success:
                print(f"✅ Trait bridges created for: {drop_id}")
            else:
                print(f"❌ Failed to create trait bridges for: {drop_id}")
        except ImportError:
            print("❌ Trait bridge module not found")
            return False

    elif action == "export":
        if not game:
            print("❌ Game parameter required for export action")
            return False

        print(f"📤 Exporting trait bridges for game: {game}")
        try:
            from xo_core.trait_bridge import export_game_implementation

            success = export_game_implementation(drop_id, game)
            if success:
                print(f"✅ Trait bridges exported for {game}")
            else:
                print(f"❌ Failed to export trait bridges for {game}")
        except ImportError:
            print("❌ Trait bridge module not found")
            return False

    else:
        print(f"❌ Unknown action: {action}")
        return False

    return True


@task
def generate_prompts(c, drop_id):
    """
    Generate GPT-5 prompt templates for traits in a drop.
    """
    print(f"📝 Generating GPT-5 prompt templates for: {drop_id}")

    script_path = Path("scripts/trait_prompt_generator.py")
    if not script_path.exists():
        print(f"❌ Trait prompt generator script not found: {script_path}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), drop_id],
            capture_output=True,
            text=True,
            check=True,
        )

        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Trait prompt generation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


@task
def dreamify(c, drop_id, style="surreal", model="midjourney"):
    """
    Turn .traits.yml into surreal storyboards using Midjourney/DALL-E prompts.

    Args:
        drop_id: The drop ID to dreamify
        style: Visual style (surreal, cosmic, ethereal, etc.)
        model: AI model (midjourney, dalle, stable-diffusion)
    """
    print(f"🌌 Dreamifying {drop_id} with {style} style for {model}")

    # Load trait data
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id,
    ]

    trait_data = {}
    for path in drop_paths:
        traits_file = path / "hidden" / ".traits.yml"
        if traits_file.exists():
            with open(traits_file, "r") as f:
                trait_data = yaml.safe_load(f)
            break

    if not trait_data:
        print(f"❌ No trait data found for drop: {drop_id}")
        return False

    # Create dreamify output directory
    dreamify_dir = Path("drops") / drop_id / "dreamify"
    dreamify_dir.mkdir(parents=True, exist_ok=True)

    # Generate storyboard prompts for each trait
    storyboards = []
    for trait_name, trait_info in trait_data.items():
        if isinstance(trait_info, dict):
            description = trait_info.get("description", "Unknown trait")
            rarity = trait_info.get("rarity", "common")

            # Create Midjourney/DALL-E style prompt
            if model == "midjourney":
                prompt = f"""Create a {style} storyboard scene featuring: {description}

                Style: {style}, cinematic lighting, detailed character design
                Mood: Mysterious and enchanting
                Rarity: {rarity} level
                Format: Wide aspect ratio, storyboard panels

                --ar 16:9 --v 6 --q 2 --s 750"""
            else:  # DALL-E style
                prompt = f"""A {style} storyboard scene showing: {description}

                Style: {style}, cinematic composition, rich details
                Mood: Mysterious and enchanting
                Rarity: {rarity} level
                Format: Storyboard with multiple panels showing progression"""

            storyboard_data = {
                "trait_name": trait_name,
                "description": description,
                "rarity": rarity,
                "model": model,
                "style": style,
                "prompt": prompt,
                "generated_at": datetime.now().isoformat(),
            }

            storyboards.append(storyboard_data)

            # Save individual prompt file
            prompt_file = dreamify_dir / f"{trait_name}_{style}_{model}.txt"
            with open(prompt_file, "w") as f:
                f.write(prompt)

    # Save storyboard bundle
    bundle_file = dreamify_dir / f"storyboards_{style}_{model}.yml"
    with open(bundle_file, "w") as f:
        yaml.dump(
            {
                "drop_id": drop_id,
                "style": style,
                "model": model,
                "generated_at": datetime.now().isoformat(),
                "storyboards": storyboards,
            },
            f,
            default_flow_style=False,
            sort_keys=False,
        )

    print(f"✅ Generated {len(storyboards)} storyboard prompts")
    print(f"📁 Saved to: {dreamify_dir}")
    return True


@task
def broadcast(c, drop_id, platforms="vault,discord", message=None):
    """
    Auto-post creative Pulse to Vault + Discord.

    Args:
        drop_id: The drop ID to broadcast
        platforms: Comma-separated platforms (vault,discord,twitter)
        message: Custom message (optional)
    """
    print(f"📡 Broadcasting {drop_id} to: {platforms}")

    # Load drop metadata
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Load status and lore
    status_file = drop_path / f"{drop_id}.status.json"
    lore_file = drop_path / ".lore.yml"

    status = {}
    lore = {}

    if status_file.exists():
        with open(status_file, "r") as f:
            status = json.load(f)

    if lore_file.exists():
        with open(lore_file, "r") as f:
            lore = yaml.safe_load(f)

    # Generate broadcast message
    if not message:
        title = status.get("title", drop_id)
        description = status.get("description", "A mysterious drop in the XO universe")

        message = f"""🌌 **XO Pulse: {title}**

{description}

🔮 Explore the lore, traits, and community conversation around this drop.
💫 No ownership required - all perspectives welcome!

#XOVerse #CreativeCommons #CommunityDriven"""

    # Create broadcast directory
    broadcast_dir = drop_path / "broadcast"
    broadcast_dir.mkdir(parents=True, exist_ok=True)

    # Generate platform-specific messages
    platforms_list = [p.strip() for p in platforms.split(",")]

    for platform in platforms_list:
        if platform == "vault":
            vault_message = f"""# XO Pulse: {drop_id}

{message}

## Quick Links
- [Drop Details](/drops/{drop_id})
- [Community Inbox](/drops/{drop_id}/inbox)
- [Trait Explorer](/drops/{drop_id}/traits)

---
*Generated by XO Agent Broadcast System*"""

            vault_file = broadcast_dir / "vault_pulse.md"
            with open(vault_file, "w") as f:
                f.write(vault_message)
            print(f"✅ Generated Vault pulse: {vault_file}")

        elif platform == "discord":
            discord_message = f"""🌌 **XO Pulse: {drop_id}**

{message}

🔗 **Links:**
• Drop: https://xo.community/drops/{drop_id}
• Inbox: https://xo.community/drops/{drop_id}/inbox
• Traits: https://xo.community/drops/{drop_id}/traits

---
*XO Agent Broadcast*"""

            discord_file = broadcast_dir / "discord_pulse.txt"
            with open(discord_file, "w") as f:
                f.write(discord_message)
            print(f"✅ Generated Discord pulse: {discord_file}")

        elif platform == "twitter":
            # Twitter has character limits
            twitter_message = f"🌌 XO Pulse: {drop_id}\n\n{message[:200]}...\n\n#XOVerse #CreativeCommons"

            twitter_file = broadcast_dir / "twitter_pulse.txt"
            with open(twitter_file, "w") as f:
                f.write(twitter_message)
            print(f"✅ Generated Twitter pulse: {twitter_file}")

    print(f"🎉 Broadcast messages generated for: {', '.join(platforms_list)}")
    return True


@task
def initiate(c, drop_id, template="community"):
    """
    Auto-populate inbox/ with call-to-action for remixing lore or traits.

    Args:
        drop_id: The drop ID to initiate
        template: Template type (community, creative, lore, traits)
    """
    print(f"📬 Initiating inbox for {drop_id} with {template} template")

    # Load drop metadata
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Create inbox directory
    inbox_dir = drop_path / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    # Load existing data
    status_file = drop_path / f"{drop_id}.status.json"
    traits_file = drop_path / "hidden" / ".traits.yml"

    status = {}
    traits = {}

    if status_file.exists():
        with open(status_file, "r") as f:
            status = json.load(f)

    if traits_file.exists():
        with open(traits_file, "r") as f:
            traits = yaml.safe_load(f)

    # Generate template-specific content
    if template == "community":
        content = f"""# 📬 {status.get('title', drop_id)} - Community Inbox

Welcome to the conversation around this drop!

## 🎯 What's This About?

{status.get('description', 'A unique drop in the XO universe with hidden depths waiting to be explored.')}

## 💭 Join the Conversation

- What story do you see in this drop?
- How might it connect to other parts of the XO universe?
- What questions would you ask the creator?

## 🧩 Traits & Lore

*Discover the hidden characteristics and backstory elements that make this drop unique.*

## 🎨 Creative Remix Challenge

**Challenge:** Create your own variation of this drop's theme or traits.

**Guidelines:**
- Build upon the existing lore respectfully
- Share your creative interpretation
- Connect to broader XO universe themes
- No ownership required - all perspectives welcome!

---

*Generated by XO Agent Inbox Initiator - {datetime.now().isoformat()}*
*Community-driven creativity without barriers*"""

    elif template == "creative":
        content = f"""# 🎨 {status.get('title', drop_id)} - Creative Workshop

## 🎭 Creative Prompt

Based on the traits and lore of this drop, create something new:

**Option 1: Visual Art**
- Draw/paint a scene inspired by this drop
- Create a character design based on the traits
- Design a new variant or evolution

**Option 2: Storytelling**
- Write a short story about this drop's origins
- Create a dialogue between characters
- Develop a prophecy or legend

**Option 3: Game Design**
- Design a new trait or ability
- Create a game mechanic inspired by this drop
- Suggest cross-game compatibility ideas

## 🧩 Available Traits

{chr(10).join([f"- **{name}**: {info.get('description', 'No description')}" for name, info in traits.items() if isinstance(info, dict)])}

## 📤 Share Your Creation

Post your work here or link to external platforms. All creative interpretations welcome!

---

*XO Creative Workshop - {datetime.now().isoformat()}*"""

    elif template == "lore":
        content = f"""# 📜 {status.get('title', drop_id)} - Lore Expansion

## 🌌 Lore Development Challenge

Help expand the mythology around this drop:

### 📝 Story Elements to Explore
- **Origins**: How did this drop come to exist?
- **Connections**: What links it to other drops in the XO universe?
- **Prophecies**: What future events might it foretell?
- **Characters**: Who might be connected to this drop?

### 🎭 Creative Writing Prompts
1. Write a legend about this drop's creation
2. Create a prophecy involving this drop
3. Develop a character who possesses this drop
4. Describe a ritual or ceremony involving this drop

### 🧩 Trait Integration
Incorporate these traits into your lore:
{chr(10).join([f"- **{name}**: {info.get('description', 'No description')}" for name, info in traits.items() if isinstance(info, dict)])}

## 📚 Lore Guidelines
- Build upon existing XO universe themes
- Maintain consistency with established lore
- Be creative and imaginative
- Respect the collaborative nature of the universe

---

*XO Lore Expansion Initiative - {datetime.now().isoformat()}*"""

    elif template == "traits":
        content = f"""# 🧬 {status.get('title', drop_id)} - Trait Evolution

## 🔬 Trait Development Workshop

Help evolve and expand the traits of this drop:

### 🎯 Current Traits
{chr(10).join([f"**{name}**: {info.get('description', 'No description')} (Rarity: {info.get('rarity', 'unknown')})" for name, info in traits.items() if isinstance(info, dict)])}

### 🧪 Trait Evolution Challenges

**Challenge 1: Variant Creation**
- Create 3 new variants of existing traits
- Suggest rarity progression (common → rare → epic → legendary)
- Design cross-game compatibility

**Challenge 2: Trait Fusion**
- Combine 2+ existing traits into new hybrid traits
- Suggest synergistic effects
- Create balanced gameplay mechanics

**Challenge 3: Trait Storytelling**
- Write backstory for how traits developed
- Create characters who embody specific traits
- Design trait-based quests or challenges

### 🎮 Game Integration Ideas
- MarioKart: Speed, stealth, and power effects
- Sims: Personality and skill enhancements
- Minecraft: Resource gathering and exploration bonuses
- Other games: Your creative suggestions!

## 📊 Submission Format
```
Trait Name: [Name]
Description: [Description]
Rarity: [common/rare/epic/legendary]
Game Effects:
  - [Game]: [Effect]
  - [Game]: [Effect]
Lore Connection: [How it fits into the universe]
```

---

*XO Trait Evolution Workshop - {datetime.now().isoformat()}*"""

    # Save the initiated inbox content
    initiated_file = inbox_dir / f"initiated_{template}.mdx"
    with open(initiated_file, "w") as f:
        f.write(content)

    print(f"✅ Created {template} inbox template: {initiated_file}")

    # Also update the main seed file
    seed_file = inbox_dir / "seed.mdx"
    if seed_file.exists():
        # Backup existing seed
        backup_file = (
            inbox_dir / f"seed_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mdx"
        )
        seed_file.rename(backup_file)
        print(f"📦 Backed up existing seed to: {backup_file}")

    # Create new enhanced seed
    with open(seed_file, "w") as f:
        f.write(content)

    print(f"✅ Updated main inbox seed with {template} template")
    return True


@task
def persona_craft(c, drop_id, blend_method="fusion"):
    """
    Build new personas directly from trait blends.

    Args:
        drop_id: The drop ID to craft personas from
        blend_method: Method for blending traits (fusion, evolution, contrast)
    """
    print(f"🧙‍♂️ Crafting personas for {drop_id} using {blend_method} method")

    # Load trait data
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id,
    ]

    trait_data = {}
    for path in drop_paths:
        traits_file = path / "hidden" / ".traits.yml"
        if traits_file.exists():
            with open(traits_file, "r") as f:
                trait_data = yaml.safe_load(f)
            break

    if not trait_data:
        print(f"❌ No trait data found for drop: {drop_id}")
        return False

    # Create personas directory
    personas_dir = Path("drops") / drop_id / "personas"
    personas_dir.mkdir(parents=True, exist_ok=True)

    # Generate personas based on blend method
    personas = []

    if blend_method == "fusion":
        # Combine all traits into a unified persona
        all_traits = list(trait_data.keys())
        if len(all_traits) >= 2:
            persona_name = f"{drop_id}_fusion_master"
            trait_descriptions = [
                trait_data[t].get("description", "")
                for t in all_traits
                if isinstance(trait_data[t], dict)
            ]

            persona_data = {
                "name": persona_name,
                "title": f"Fusion Master of {drop_id}",
                "description": f"A being who embodies all aspects of {drop_id}: {'; '.join(trait_descriptions)}",
                "traits": all_traits,
                "personality": "Balanced, harmonious, masterful",
                "specialty": "Trait synthesis and cosmic balance",
                "blend_method": blend_method,
                "created_at": datetime.now().isoformat(),
            }
            personas.append(persona_data)

    elif blend_method == "evolution":
        # Create evolved versions of each trait
        for trait_name, trait_info in trait_data.items():
            if isinstance(trait_info, dict):
                evolved_name = f"{trait_name}_evolved"
                persona_data = {
                    "name": evolved_name,
                    "title": f"Evolved {trait_name.title()}",
                    "description": f"An evolved form of {trait_info.get('description', trait_name)}",
                    "base_trait": trait_name,
                    "evolution_stage": "evolved",
                    "personality": "Advanced, refined, powerful",
                    "specialty": f"Mastery of {trait_name} abilities",
                    "blend_method": blend_method,
                    "created_at": datetime.now().isoformat(),
                }
                personas.append(persona_data)

    elif blend_method == "contrast":
        # Create contrasting personas
        trait_list = list(trait_data.keys())
        for i, trait_name in enumerate(trait_list):
            if isinstance(trait_data[trait_name], dict):
                # Find contrasting trait
                contrast_trait = trait_list[(i + 1) % len(trait_list)]
                contrast_name = f"{trait_name}_vs_{contrast_trait}"

                persona_data = {
                    "name": contrast_name,
                    "title": f"Contrast: {trait_name.title()} vs {contrast_trait.title()}",
                    "description": f"A being caught between {trait_data[trait_name].get('description', trait_name)} and {trait_data[contrast_trait].get('description', contrast_trait)}",
                    "traits": [trait_name, contrast_trait],
                    "personality": "Conflicted, dynamic, transformative",
                    "specialty": "Trait conflict resolution and synthesis",
                    "blend_method": blend_method,
                    "created_at": datetime.now().isoformat(),
                }
                personas.append(persona_data)

    # Save personas
    for persona in personas:
        persona_file = personas_dir / f"{persona['name']}.yml"
        with open(persona_file, "w") as f:
            yaml.dump(persona, f, default_flow_style=False, sort_keys=False)

    # Create persona index
    index_data = {
        "drop_id": drop_id,
        "blend_method": blend_method,
        "generated_at": datetime.now().isoformat(),
        "personas": [p["name"] for p in personas],
    }

    index_file = personas_dir / "persona_index.yml"
    with open(index_file, "w") as f:
        yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created {len(personas)} personas using {blend_method} method")
    print(f"📁 Saved to: {personas_dir}")
    return True


@task
def constellation_link(c, drop_id, add_to_index=True):
    """
    Add the drop to /constellation/index.yml to grow the XO Lore Map.

    Args:
        drop_id: The drop ID to link
        add_to_index: Whether to add to the main constellation index
    """
    print(f"🗺️ Linking {drop_id} to XO Constellation")

    # Load drop metadata
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Load status and traits
    status_file = drop_path / f"{drop_id}.status.json"
    traits_file = drop_path / "hidden" / ".traits.yml"

    status = {}
    traits = {}

    if status_file.exists():
        with open(status_file, "r") as f:
            status = json.load(f)

    if traits_file.exists():
        with open(traits_file, "r") as f:
            traits = yaml.safe_load(f)

    # Create constellation data
    constellation_data = {
        "drop_id": drop_id,
        "title": status.get("title", drop_id),
        "description": status.get("description", "A drop in the XO universe"),
        "tags": status.get("tags", []),
        "traits": list(traits.keys()) if traits else [],
        "rarity_levels": list(
            set(
                [
                    t.get("rarity", "common")
                    for t in traits.values()
                    if isinstance(t, dict)
                ]
            )
        ),
        "connections": [],
        "coordinates": {
            "x": hash(drop_id) % 1000,  # Simple hash-based positioning
            "y": hash(drop_id[::-1]) % 1000,
        },
        "linked_at": datetime.now().isoformat(),
    }

    # Create constellation directory
    constellation_dir = Path("constellation")
    constellation_dir.mkdir(parents=True, exist_ok=True)

    # Save individual drop constellation file
    drop_constellation_file = constellation_dir / f"{drop_id}.yml"
    with open(drop_constellation_file, "w") as f:
        yaml.dump(constellation_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created constellation file: {drop_constellation_file}")

    # Update main constellation index
    if add_to_index:
        index_file = constellation_dir / "index.yml"

        # Load existing index or create new one
        if index_file.exists():
            with open(index_file, "r") as f:
                index_data = yaml.safe_load(f) or {}
        else:
            index_data = {
                "name": "XO Constellation",
                "description": "Living map of XO universe connections",
                "created_at": datetime.now().isoformat(),
                "drops": [],
            }

        # Add drop to index if not already present
        existing_drops = [d.get("drop_id") for d in index_data.get("drops", [])]
        if drop_id not in existing_drops:
            index_data["drops"].append(constellation_data)
            index_data["updated_at"] = datetime.now().isoformat()

            with open(index_file, "w") as f:
                yaml.dump(index_data, f, default_flow_style=False, sort_keys=False)

            print(f"✅ Added {drop_id} to constellation index")
        else:
            print(f"ℹ️ {drop_id} already in constellation index")

    # Generate constellation visualization data
    viz_data = {
        "nodes": [
            {
                "id": drop_id,
                "label": status.get("title", drop_id),
                "group": "drops",
                "x": constellation_data["coordinates"]["x"],
                "y": constellation_data["coordinates"]["y"],
            }
        ],
        "edges": [],
        "metadata": {
            "total_drops": len(index_data.get("drops", [])) if add_to_index else 1,
            "generated_at": datetime.now().isoformat(),
        },
    }

    viz_file = constellation_dir / f"{drop_id}_visualization.json"
    with open(viz_file, "w") as f:
        json.dump(viz_data, f, indent=2)

    print(f"✅ Generated visualization data: {viz_file}")
    print(f"🗺️ {drop_id} successfully linked to XO Constellation")
    return True


@task
def drop_regen(c, drop_id, version="v2", evolution_type="fusion"):
    """
    Create an evolved drop version over time (e.g. message_bottle → message_bottle_v2).

    Args:
        drop_id: The original drop ID to evolve
        version: Version suffix (v2, v3, evolved, etc.)
        evolution_type: Type of evolution (fusion, contrast, cosmic, remix)
    """
    print(f"🔄 Regenerating {drop_id} into {drop_id}_{version} with {evolution_type} evolution")

    # Create new drop directory
    new_drop_id = f"{drop_id}_{version}"
    new_drop_path = Path("drops") / new_drop_id
    new_drop_path.mkdir(parents=True, exist_ok=True)

    # Load original drop data
    original_path = Path("drops") / drop_id
    if not original_path.exists():
        print(f"❌ Original drop not found: {drop_id}")
        return False

    # Copy and evolve traits
    original_traits_file = original_path / "hidden" / ".traits.yml"
    new_traits_file = new_drop_path / "hidden" / ".traits.yml"
    new_traits_file.parent.mkdir(parents=True, exist_ok=True)

    if original_traits_file.exists():
        with open(original_traits_file, 'r') as f:
            original_traits = yaml.safe_load(f)

        # Evolve traits based on evolution type
        evolved_traits = {}

        if evolution_type == "fusion":
            # Combine traits into new hybrid forms
            trait_names = list(original_traits.keys())
            for i in range(0, len(trait_names), 2):
                if i + 1 < len(trait_names):
                    trait1 = trait_names[i]
                    trait2 = trait_names[i + 1]
                    fusion_name = f"{trait1}_{trait2}_fusion"

                    evolved_traits[fusion_name] = {
                        "description": f"Fusion of {original_traits[trait1].get('description', trait1)} and {original_traits[trait2].get('description', trait2)}",
                        "rarity": "epic",
                        "evolution_source": [trait1, trait2],
                        "game_effects": {
                            "mario_kart": {"fusion_boost": 0.25},
                            "sims": {"fusion_creativity": 3},
                            "minecraft": {"fusion_mining": 1.5}
                        }
                    }

        elif evolution_type == "contrast":
            # Create contrasting versions
            for trait_name, trait_data in original_traits.items():
                contrast_name = f"{trait_name}_contrast"
                evolved_traits[contrast_name] = {
                    "description": f"Contrasting evolution of {trait_data.get('description', trait_name)}",
                    "rarity": "rare",
                    "evolution_source": [trait_name],
                    "game_effects": {
                        "mario_kart": {"contrast_speed": 0.2},
                        "sims": {"contrast_charisma": 2},
                        "minecraft": {"contrast_jump": 2.0}
                    }
                }

        elif evolution_type == "cosmic":
            # Cosmic evolution with enhanced effects
            for trait_name, trait_data in original_traits.items():
                cosmic_name = f"{trait_name}_cosmic"
                evolved_traits[cosmic_name] = {
                    "description": f"Cosmic evolution of {trait_data.get('description', trait_name)} - transcending mortal limitations",
                    "rarity": "legendary",
                    "evolution_source": [trait_name],
                    "game_effects": {
                        "mario_kart": {"cosmic_gravity": 3.0, "cosmic_shield": 30},
                        "sims": {"cosmic_inspiration": 5, "cosmic_aura": 15},
                        "minecraft": {"cosmic_vision": 600, "cosmic_finder": 100}
                    }
                }

        elif evolution_type == "remix":
            # Creative remix with new combinations
            trait_names = list(original_traits.keys())
            for i, trait_name in enumerate(trait_names):
                remix_name = f"{trait_name}_remix"
                evolved_traits[remix_name] = {
                    "description": f"Creative remix of {original_traits[trait_name].get('description', trait_name)} with new possibilities",
                    "rarity": "rare",
                    "evolution_source": [trait_name],
                    "remix_elements": ["community", "collaboration", "innovation"],
                    "game_effects": {
                        "mario_kart": {"remix_boost": 0.15},
                        "sims": {"remix_creativity": 2},
                        "minecraft": {"remix_speed": 1.3}
                    }
                }

        elif evolution_type == "legendary":
            # Legendary ascension with ultimate effects
            for trait_name, trait_data in original_traits.items():
                legendary_name = f"{trait_name}_legendary"
                evolved_traits[legendary_name] = {
                    "description": f"Legendary ascension of {trait_data.get('description', trait_name)} - achieving ultimate form",
                    "rarity": "legendary",
                    "evolution_source": [trait_name],
                    "legendary_powers": ["transcendence", "omniscience", "creation"],
                    "game_effects": {
                        "mario_kart": {"legendary_speed": 5.0, "legendary_shield": 60, "legendary_gravity": 5.0},
                        "sims": {"legendary_inspiration": 10, "legendary_aura": 30, "legendary_creativity": 10},
                        "minecraft": {"legendary_vision": 1000, "legendary_finder": 200, "legendary_mining": 3.0}
                    }
                }

        # Save evolved traits
        with open(new_traits_file, 'w') as f:
            yaml.dump(evolved_traits, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Created {len(evolved_traits)} evolved traits")

    # Create evolved drop metadata
    evolution_data = {
        "drop_id": new_drop_id,
        "original_drop": drop_id,
        "evolution_type": evolution_type,
        "version": version,
        "evolved_at": datetime.now().isoformat(),
        "evolution_description": f"Evolved version of {drop_id} using {evolution_type} evolution",
        "traits_evolved": len(evolved_traits) if 'evolved_traits' in locals() else 0
    }

    # Save evolution metadata
    evolution_file = new_drop_path / f"{new_drop_id}.evolution.yml"
    with open(evolution_file, 'w') as f:
        yaml.dump(evolution_data, f, default_flow_style=False, sort_keys=False)

    # Create evolved drop content
    content_file = new_drop_path / f"{new_drop_id}.mdx"
    content = f"""# {new_drop_id.title()}

## 🌌 Evolution Story

This is an evolved version of **{drop_id}**, created through **{evolution_type}** evolution.

### 🔄 Evolution Details

- **Original Drop**: {drop_id}
- **Evolution Type**: {evolution_type}
- **Version**: {version}
- **Evolved At**: {evolution_data['evolved_at']}

### 🧬 Evolved Traits

This drop contains {evolution_data['traits_evolved']} evolved traits, each representing a new possibility in the XO universe.

### 🎨 Creative Possibilities

- **Visual Evolution**: Generate new art with evolved traits
- **Lore Expansion**: Explore the story of this evolution
- **Community Remix**: Create your own variations
- **Game Integration**: Experience evolved traits in different worlds

---

*Generated by XO Drop Regen System - {datetime.now().isoformat()}*
*Part of the living XO universe evolution*"""

    with open(content_file, 'w') as f:
        f.write(content)

    print(f"✅ Created evolved drop: {new_drop_id}")
    print(f"📁 Location: {new_drop_path}")

    return new_drop_id


@task
def vault_showcase(c, drop_id, showcase_type="full"):
    """
    Generate complete showcase content for a drop including visuals, broadcasts, and constellation links.

    Args:
        drop_id: The drop ID to showcase
        showcase_type: Type of showcase (full, visual, social, constellation)
    """
    print(f"🎨 Creating {showcase_type} showcase for {drop_id}")

    # Create showcase directory
    showcase_dir = Path("drops") / drop_id / "showcase"
    showcase_dir.mkdir(parents=True, exist_ok=True)

    if showcase_type in ["full", "visual"]:
        # Generate visual content
        print("🌌 Generating visual content...")
        dreamify_result = subprocess.run([
            sys.executable, "-m", "xo_core.fab_tasks.agent_tasks", "dreamify",
            "--drop-id", drop_id, "--style", "cosmic", "--model", "midjourney"
        ], capture_output=True, text=True)

        if dreamify_result.returncode == 0:
            print("✅ Visual prompts generated")
        else:
            print("⚠️ Visual generation had issues")

    if showcase_type in ["full", "social"]:
        # Generate social content
        print("📡 Generating social content...")
        broadcast_result = subprocess.run([
            sys.executable, "-m", "xo_core.fab_tasks.agent_tasks", "broadcast",
            "--drop-id", drop_id, "--platforms", "vault,discord,twitter"
        ], capture_output=True, text=True)

        if broadcast_result.returncode == 0:
            print("✅ Social content generated")
        else:
            print("⚠️ Social generation had issues")

    if showcase_type in ["full", "constellation"]:
        # Link to constellation
        print("🗺️ Linking to constellation...")
        constellation_result = subprocess.run([
            sys.executable, "-m", "xo_core.fab_tasks.agent_tasks", "constellation-link",
            "--drop-id", drop_id
        ], capture_output=True, text=True)

        if constellation_result.returncode == 0:
            print("✅ Constellation link created")
        else:
            print("⚠️ Constellation linking had issues")

    # Create showcase index
    showcase_index = {
        "drop_id": drop_id,
        "showcase_type": showcase_type,
        "created_at": datetime.now().isoformat(),
        "components": {
            "visual": showcase_type in ["full", "visual"],
            "social": showcase_type in ["full", "social"],
            "constellation": showcase_type in ["full", "constellation"]
        },
        "files": {
            "dreamify": list((Path("drops") / drop_id / "dreamify").glob("*.txt")) if (Path("drops") / drop_id / "dreamify").exists() else [],
            "broadcast": list((Path("drops") / drop_id / "broadcast").glob("*")) if (Path("drops") / drop_id / "broadcast").exists() else [],
            "constellation": list(Path("constellation").glob(f"{drop_id}*")) if Path("constellation").exists() else []
        }
    }

    index_file = showcase_dir / "showcase_index.yml"
    with open(index_file, 'w') as f:
        yaml.dump(showcase_index, f, default_flow_style=False, sort_keys=False)

    # Create showcase README
    readme_content = f"""# {drop_id.title()} - XO Showcase

## 🎨 Showcase Overview

This showcase contains all generated content for **{drop_id}** in the XO universe.

### 📁 Contents

- **Visual Prompts**: AI art generation prompts for Midjourney/DALL-E
- **Social Content**: Ready-to-post messages for various platforms
- **Constellation Data**: Universe mapping and connection data
- **Trait Bridges**: Cross-game compatibility definitions

### 🚀 Quick Start

1. **Generate Art**: Use the prompts in `dreamify/` with your preferred AI art tool
2. **Share Content**: Post the content in `broadcast/` to your platforms
3. **Explore Connections**: Check `constellation/` for universe connections
4. **Game Integration**: Use `bridges/` for cross-game trait implementation

### 🌌 Creative Possibilities

- Create visual variations using the generated prompts
- Share the drop story across social platforms
- Connect this drop to others in the XO constellation
- Implement traits in your favorite games

---

*XO Showcase System - {datetime.now().isoformat()}*
*Part of the living XO creative ecosystem*"""

    readme_file = showcase_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)

    print(f"✅ Created {showcase_type} showcase for {drop_id}")
    print(f"📁 Showcase location: {showcase_dir}")
    return True


@task
def react(c, drop_id, persona="vault_keeper", auto_reply=True):
    """
    React to inbox replies using personas.

    Args:
        drop_id: The drop ID to react to
        persona: Persona to use for reactions
        auto_reply: Whether to generate automatic replies
    """
    print(f"🔁 Reacting to {drop_id} inbox with {persona} persona")

    # Load inbox content
    inbox_dir = Path("drops") / drop_id / "inbox"
    if not inbox_dir.exists():
        print(f"❌ Inbox not found for: {drop_id}")
        return False

    # Load persona data
    personas_dir = Path("drops") / drop_id / "personas"
    persona_file = personas_dir / f"{persona}.yml"

    persona_data = {}
    if persona_file.exists():
        with open(persona_file, 'r') as f:
            persona_data = yaml.safe_load(f)

    # Generate reaction content
    reaction_content = f"""# 🤖 {persona.title()} Reacts to {drop_id}

## 🎭 Persona Context

**{persona_data.get('title', persona)}**: {persona_data.get('description', 'A mysterious entity in the XO universe')}

## 💭 Reaction

*{persona_data.get('personality', 'Thoughtful and engaging')}*

### 🎯 Key Insights

- **Connection**: How this drop connects to the broader XO universe
- **Potential**: Creative possibilities and evolution pathways
- **Community**: Ways to engage and collaborate with others

### 🌟 Suggested Actions

1. **Explore Further**: Dive deeper into the lore and traits
2. **Create Together**: Collaborate on new variations
3. **Share Stories**: Connect with other community members
4. **Evolve**: Consider how this drop might grow and change

---

*Generated by XO Agent React System - {datetime.now().isoformat()}*
*Persona: {persona}*"""

    # Save reaction
    reaction_file = inbox_dir / f"reaction_{persona}.mdx"
    with open(reaction_file, 'w') as f:
        f.write(reaction_content)

    print(f"✅ Generated reaction from {persona} persona")
    return True


@task
def morph(c, drop_id, morph_type="trait", duration="timeline"):
    """
    Morph traits/images over time.

    Args:
        drop_id: The drop ID to morph
        morph_type: Type of morphing (trait, image, lore)
        duration: Duration of morphing (timeline, instant, gradual)
    """
    print(f"🧬 Morphing {drop_id} with {morph_type} morphing over {duration}")

    # Load trait data
    traits_file = Path("drops") / drop_id / "hidden" / ".traits.yml"
    if not traits_file.exists():
        print(f"❌ Traits not found for: {drop_id}")
        return False

    with open(traits_file, 'r') as f:
        traits = yaml.safe_load(f)

    # Create morphing directory
    morph_dir = Path("drops") / drop_id / "morph"
    morph_dir.mkdir(parents=True, exist_ok=True)

    # Generate morphing timeline
    morph_timeline = {
        "drop_id": drop_id,
        "morph_type": morph_type,
        "duration": duration,
        "created_at": datetime.now().isoformat(),
        "timeline": []
    }

    if morph_type == "trait":
        # Create trait evolution timeline
        for trait_name, trait_data in traits.items():
            if isinstance(trait_data, dict):
                evolution_stages = [
                    {
                        "stage": "original",
                        "description": trait_data.get("description", ""),
                        "rarity": trait_data.get("rarity", "common"),
                        "effects": trait_data.get("game_effects", {})
                    },
                    {
                        "stage": "evolved",
                        "description": f"Evolved {trait_data.get('description', trait_name)}",
                        "rarity": "rare",
                        "effects": {
                            "mario_kart": {"evolved_boost": 0.2},
                            "sims": {"evolved_creativity": 3},
                            "minecraft": {"evolved_speed": 1.4}
                        }
                    },
                    {
                        "stage": "legendary",
                        "description": f"Legendary {trait_data.get('description', trait_name)}",
                        "rarity": "legendary",
                        "effects": {
                            "mario_kart": {"legendary_boost": 0.5},
                            "sims": {"legendary_creativity": 5},
                            "minecraft": {"legendary_speed": 2.0}
                        }
                    }
                ]

                morph_timeline["timeline"].append({
                    "trait_name": trait_name,
                    "evolution_stages": evolution_stages
                })

    # Save morphing timeline
    timeline_file = morph_dir / f"morph_timeline_{morph_type}.yml"
    with open(timeline_file, 'w') as f:
        yaml.dump(morph_timeline, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created {morph_type} morphing timeline")
    return True


@task
def autopilot(c, trigger="publish", action="deploy"):
    """
    Trigger automation on publish.

    Args:
        trigger: Trigger event (publish, vault_update, inbox_reply)
        action: Action to take (deploy, broadcast, compile)
    """
    print(f"🔄 Autopilot triggered by {trigger}, executing {action}")

    # Create autopilot log
    autopilot_dir = Path("autopilot")
    autopilot_dir.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "trigger": trigger,
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "status": "executing"
    }

    if trigger == "publish" and action == "deploy":
        # Simulate deployment automation
        log_entry["actions"] = [
            "Build drop package",
            "Generate preview assets",
            "Update constellation index",
            "Deploy to production",
            "Broadcast to social platforms"
        ]
        log_entry["status"] = "completed"

    elif trigger == "vault_update" and action == "broadcast":
        # Simulate broadcast automation
        log_entry["actions"] = [
            "Generate social content",
            "Post to Discord",
            "Update Twitter",
            "Send Vault pulse"
        ]
        log_entry["status"] = "completed"

    elif trigger == "inbox_reply" and action == "compile":
        # Simulate compilation automation
        log_entry["actions"] = [
            "Collect inbox responses",
            "Generate digest",
            "Update lore timeline",
            "Create community summary"
        ]
        log_entry["status"] = "completed"

    # Save autopilot log
    log_file = autopilot_dir / f"autopilot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
    with open(log_file, 'w') as f:
        yaml.dump(log_entry, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Autopilot {action} completed for {trigger}")
    return True


@task
def portal(c, drop_id, format="iframe"):
    """
    Generate iframe-compatible HTML for embedded drops.

    Args:
        drop_id: The drop ID to create portal for
        format: Output format (iframe, embed, widget)
    """
    print(f"🌀 Creating {format} portal for {drop_id}")

    # Load drop data
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Load content
    content_file = drop_path / f"{drop_id}.mdx"
    traits_file = drop_path / "hidden" / ".traits.yml"

    content = ""
    traits = {}

    if content_file.exists():
        with open(content_file, 'r') as f:
            content = f.read()

    if traits_file.exists():
        with open(traits_file, 'r') as f:
            traits = yaml.safe_load(f)

    # Create portal directory
    portal_dir = drop_path / "portal"
    portal_dir.mkdir(parents=True, exist_ok=True)

    if format == "iframe":
        # Generate iframe-compatible HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XO Drop: {drop_id}</title>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .drop-container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        .drop-title {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 20px;
            text-align: center;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .drop-content {{
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .traits-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }}
        .trait-item {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }}
        .trait-name {{
            font-weight: 600;
            color: #4ecdc4;
        }}
        .trait-description {{
            margin-top: 5px;
            opacity: 0.9;
        }}
        .xo-brand {{
            text-align: center;
            margin-top: 30px;
            opacity: 0.7;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="drop-container">
        <h1 class="drop-title">{drop_id.replace('_', ' ').title()}</h1>

        <div class="drop-content">
            {content.replace('#', '<h2>').replace(chr(10) + chr(10), '</h2>' + chr(10) + chr(10))}
        </div>

        <div class="traits-section">
            <h3>🧬 Traits</h3>
            {chr(10).join([f'<div class="trait-item"><div class="trait-name">{name}</div><div class="trait-description">{info.get("description", "No description")}</div></div>' for name, info in traits.items() if isinstance(info, dict)])}
        </div>

        <div class="xo-brand">
            🌌 XO Universe Portal • Generated by XO Agent System
        </div>
    </div>
</body>
</html>"""

        portal_file = portal_dir / f"{drop_id}_portal.html"
        with open(portal_file, 'w') as f:
            f.write(html_content)

        print(f"✅ Created iframe portal: {portal_file}")

    elif format == "embed":
        # Generate embed code
        embed_code = f"""<!-- XO Drop Embed: {drop_id} -->
<iframe
    src="https://xo-vault.com/drops/{drop_id}/portal/{drop_id}_portal.html"
    width="100%"
    height="600"
    frameborder="0"
    style="border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
</iframe>
<!-- End XO Drop Embed -->"""

        embed_file = portal_dir / f"{drop_id}_embed.html"
        with open(embed_file, 'w') as f:
            f.write(embed_code)

        print(f"✅ Created embed code: {embed_file}")

    return True


@task
def enable_enhancements(c, target="all"):
    """
    Enable all agent enhancements.

    Args:
        target: Target enhancements (all, react, morph, autopilot, portal)
    """
    print(f"🔧 Enabling {target} agent enhancements")

    # Create enhancements directory
    enhancements_dir = Path("enhancements")
    enhancements_dir.mkdir(parents=True, exist_ok=True)

    enhancements = {
        "react": "Inbox responder with persona-driven reactions",
        "morph": "Trait and content evolution over time",
        "autopilot": "Automated deployment and publishing",
        "portal": "Web-embeddable drop previews"
    }

    enabled_features = []

    if target == "all" or target == "react":
        enabled_features.append("react")
        print("✅ Enabled: Inbox responder")

    if target == "all" or target == "morph":
        enabled_features.append("morph")
        print("✅ Enabled: Trait animator")

    if target == "all" or target == "autopilot":
        enabled_features.append("autopilot")
        print("✅ Enabled: Auto-package deployer")

    if target == "all" or target == "portal":
        enabled_features.append("portal")
        print("✅ Enabled: Web portal drop preview")

    # Save enhancement status
    status_file = enhancements_dir / "enabled_features.yml"
    with open(status_file, 'w') as f:
        yaml.dump({
            "enabled_at": datetime.now().isoformat(),
            "enabled_features": enabled_features,
            "feature_descriptions": enhancements
        }, f, default_flow_style=False, sort_keys=False)

    print(f"🎉 Enabled {len(enabled_features)} agent enhancements")
    return True


@task
def constellation_feed(c, output_dir="vault/daily"):
    """
    Generate daily lore digest from constellation-linked drops.

    Args:
        output_dir: Directory to save daily digest
    """
    print(f"📰 Generating constellation feed for daily digest")

    # Load constellation index
    constellation_dir = Path("constellation")
    index_file = constellation_dir / "index.yml"

    if not index_file.exists():
        print(f"❌ Constellation index not found")
        return False

    with open(index_file, 'r') as f:
        constellation_data = yaml.safe_load(f)

    # Create daily digest directory
    daily_dir = Path(output_dir)
    daily_dir.mkdir(parents=True, exist_ok=True)

    # Generate daily digest
    today = datetime.now().strftime("%Y-%m-%d")
    digest_content = f"""# 🌌 XO Daily Digest - {today}

## 📊 Constellation Overview

**Total Drops**: {len(constellation_data.get('drops', []))}
**Last Updated**: {constellation_data.get('updated_at', 'Unknown')}

## 🗺️ Universe Connections

"""

    # Add each drop to digest
    for drop in constellation_data.get('drops', []):
        drop_id = drop.get('drop_id', 'Unknown')
        title = drop.get('title', drop_id)
        description = drop.get('description', 'A drop in the XO universe')
        traits = drop.get('traits', [])

        digest_content += f"""### 📦 {title}

{description}

**Traits**: {', '.join(traits) if traits else 'None'}
**Rarity Levels**: {', '.join(drop.get('rarity_levels', []))}

---
"""

    digest_content += f"""
## 🌟 Today's Highlights

- **New Connections**: {len(constellation_data.get('drops', []))} drops in the constellation
- **Community Activity**: Check inboxes for community engagement
- **Evolution Paths**: Explore trait bridges and game compatibility

## 🔗 Quick Links

- [Constellation Map](/constellation)
- [Community Inboxes](/drops/*/inbox)
- [Trait Explorer](/drops/*/traits)

---

*Generated by XO Constellation Feed - {datetime.now().isoformat()}*
*Part of the living XO universe*"""

    # Save daily digest
    digest_file = daily_dir / f"digest_{today}.mdx"
    with open(digest_file, 'w') as f:
        f.write(digest_content)

    print(f"✅ Generated daily digest: {digest_file}")
    return True


@task
def pulse_new(c, pulse_type="lore_update", content=None):
    """
    Create a new pulse for the XO universe.

    Args:
        pulse_type: Type of pulse (lore_update, drop_evolution, community_highlight)
        content: Custom content for the pulse
    """
    print(f"📡 Creating new {pulse_type} pulse")

    # Create pulses directory
    pulses_dir = Path("pulses")
    pulses_dir.mkdir(parents=True, exist_ok=True)

    # Generate pulse content
    if not content:
        if pulse_type == "lore_update":
            content = f"""🌌 **XO Lore Update**

The XO universe continues to evolve with new connections and discoveries.

**Latest Developments:**
- New drops added to the constellation
- Community engagement in inboxes
- Trait evolution and game compatibility

**What's Next:**
- Explore new lore connections
- Participate in community discussions
- Create your own variations

#XOVerse #LoreUpdate #CommunityDriven"""

        elif pulse_type == "drop_evolution":
            content = f"""🔄 **Drop Evolution Alert**

A new evolution has occurred in the XO universe!

**Evolution Details:**
- Traits have evolved to new forms
- Game compatibility enhanced
- New personas created

**Join the Evolution:**
- Explore evolved traits
- Test game compatibility
- Create your own variations

#XOVerse #DropEvolution #TraitBridges"""

        elif pulse_type == "community_highlight":
            content = f"""🌟 **Community Highlight**

Amazing community activity in the XO universe!

**Community Achievements:**
- Creative remixes and variations
- Lore expansion and storytelling
- Cross-game trait implementation

**Get Involved:**
- Share your creations
- Connect with other creators
- Explore community inboxes

#XOVerse #CommunityHighlight #CreativeCommons"""

    # Create pulse file
    pulse_id = f"{pulse_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pulse_file = pulses_dir / f"{pulse_id}.yml"

    pulse_data = {
        "pulse_id": pulse_id,
        "type": pulse_type,
        "content": content,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    with open(pulse_file, 'w') as f:
        yaml.dump(pulse_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Created pulse: {pulse_file}")
    return True


@task
def pulse_sync(c, platforms="vault,discord"):
    """
    Sync pulses to various platforms.

    Args:
        platforms: Comma-separated platforms to sync to
    """
    print(f"🔄 Syncing pulses to: {platforms}")

    # Load pulses
    pulses_dir = Path("pulses")
    if not pulses_dir.exists():
        print(f"❌ No pulses directory found")
        return False

    # Find active pulses
    active_pulses = []
    for pulse_file in pulses_dir.glob("*.yml"):
        with open(pulse_file, 'r') as f:
            pulse_data = yaml.safe_load(f)
            if pulse_data.get('status') == 'active':
                active_pulses.append(pulse_data)

    if not active_pulses:
        print(f"ℹ️ No active pulses found")
        return False

    # Create sync directory
    sync_dir = Path("pulses/sync")
    sync_dir.mkdir(parents=True, exist_ok=True)

    platforms_list = [p.strip() for p in platforms.split(",")]

    for platform in platforms_list:
        platform_content = f"""# XO Pulse Sync - {platform.upper()}

## 📡 Active Pulses

"""

        for pulse in active_pulses:
            platform_content += f"""### {pulse['type'].replace('_', ' ').title()}

{pulse['content']}

**Created**: {pulse['created_at']}

---
"""

        platform_content += f"""
## 🔗 Platform Links

- **Vault**: https://xo-vault.com
- **Constellation**: https://xo-ledger.com/constellation
- **Community**: https://xo-community.com

---

*XO Pulse Sync - {datetime.now().isoformat()}*"""

        # Save platform-specific sync
        sync_file = sync_dir / f"sync_{platform}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(sync_file, 'w') as f:
            f.write(platform_content)

        print(f"✅ Synced to {platform}: {sync_file}")

    print(f"🎉 Synced {len(active_pulses)} pulses to {len(platforms_list)} platforms")
    return True


@task
def deploy_drop_url(c, drop_id, target="public", domain="xo-vault.com"):
    """
    Deploy a drop to a public URL with full frontend integration.

    Args:
        drop_id: The drop ID to deploy
        target: Deployment target (public, staging, preview)
        domain: Target domain for deployment
    """
    print(f"🚀 Deploying {drop_id} to {target} on {domain}")

    # Load drop data
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Create deployment directory
    deploy_dir = Path("deploy") / target / drop_id
    deploy_dir.mkdir(parents=True, exist_ok=True)

    # Load drop content
    content_file = drop_path / f"{drop_id}.mdx"
    traits_file = drop_path / "hidden" / ".traits.yml"
    portal_file = drop_path / "portal" / f"{drop_id}_portal.html"

    content = ""
    traits = {}

    if content_file.exists():
        with open(content_file, 'r') as f:
            content = f.read()

    if traits_file.exists():
        with open(traits_file, 'r') as f:
            traits = yaml.safe_load(f)

    # Generate deployment configuration
    deploy_config = {
        "drop_id": drop_id,
        "target": target,
        "domain": domain,
        "deployed_at": datetime.now().isoformat(),
        "url": f"https://{domain}/drops/{drop_id}",
        "assets": {
            "content": str(content_file) if content_file.exists() else None,
            "traits": str(traits_file) if traits_file.exists() else None,
            "portal": str(portal_file) if portal_file.exists() else None
        }
    }

    # Save deployment config
    config_file = deploy_dir / "deploy_config.yml"
    with open(config_file, 'w') as f:
        yaml.dump(deploy_config, f, default_flow_style=False, sort_keys=False)

    # Generate public page HTML
    public_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XO Drop: {drop_id.replace('_', ' ').title()}</title>
    <meta name="description" content="A drop in the XO universe - {drop_id}">
    <meta property="og:title" content="XO Drop: {drop_id.replace('_', ' ').title()}">
    <meta property="og:description" content="A drop in the XO universe">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://{domain}/drops/{drop_id}">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        .drop-header {{
            text-align: center;
            margin-bottom: 60px;
        }}
        .drop-title {{
            font-size: 3.5em;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .drop-subtitle {{
            font-size: 1.2em;
            opacity: 0.8;
            margin-bottom: 40px;
        }}
        .drop-content {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            line-height: 1.6;
        }}
        .traits-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }}
        .trait-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .trait-name {{
            font-weight: 600;
            color: #4ecdc4;
            margin-bottom: 10px;
        }}
        .trait-description {{
            opacity: 0.9;
            margin-bottom: 15px;
        }}
        .trait-rarity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 500;
            background: rgba(255, 255, 255, 0.1);
        }}
        .mint-section {{
            text-align: center;
            margin-top: 60px;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
        }}
        .mint-button {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border: none;
            color: white;
            padding: 20px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="drop-header">
            <h1 class="drop-title">{drop_id.replace('_', ' ').title()}</h1>
            <p class="drop-subtitle">A drop in the XO universe</p>
        </div>

        <div class="drop-content">
            {content.replace('#', '<h2>').replace(chr(10) + chr(10), '</h2>' + chr(10) + chr(10))}

            <div class="traits-grid">
                {chr(10).join([f'<div class="trait-card"><div class="trait-name">{name}</div><div class="trait-description">{info.get("description", "No description")}</div><span class="trait-rarity">{info.get("rarity", "common")}</span></div>' for name, info in traits.items() if isinstance(info, dict)])}
            </div>
        </div>

        <div class="mint-section">
            <h2>🌌 Mint This Drop</h2>
            <p>Join the XO universe and own a piece of this drop</p>
            <button class="mint-button" onclick="mintDrop()">Mint Drop</button>
        </div>

        <div class="xo-brand">
            🌌 XO Universe • Generated by XO Agent System
        </div>
    </div>

    <script>
        async function mintDrop() {{
            try {{
                const response = await fetch(`/api/mint?drop_id={drop_id}`);
                const result = await response.json();
                if (result.success) {{
                    alert(`Minted successfully! Transaction: ${{result.hash}}`);
                }} else {{
                    alert('Minting failed: ' + result.error);
                }}
            }} catch (error) {{
                alert('Minting failed: ' + error.message);
            }}
        }}
    </script>
</body>
</html>"""

    # Save public page
    public_file = deploy_dir / "index.html"
    with open(public_file, 'w') as f:
        f.write(public_html)

    print(f"✅ Deployed {drop_id} to {target}")
    print(f"📁 Public URL: https://{domain}/drops/{drop_id}")
    print(f"📁 Files: {deploy_dir}")

    return True


@task
def drop_bundle(c, drop_id, template="mintable"):
    """
    Bundle a drop for minting with all necessary metadata and assets.

    Args:
        drop_id: The drop ID to bundle
        template: Bundle template (mintable, community, legendary)
    """
    print(f"📦 Bundling {drop_id} with {template} template")

    # Load drop data
    drop_path = Path("drops") / drop_id
    if not drop_path.exists():
        print(f"❌ Drop not found: {drop_id}")
        return False

    # Create bundle directory
    bundle_dir = Path("bundles") / drop_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Load traits and content
    traits_file = drop_path / "hidden" / ".traits.yml"
    content_file = drop_path / f"{drop_id}.mdx"

    traits = {}
    content = ""

    if traits_file.exists():
        with open(traits_file, 'r') as f:
            traits = yaml.safe_load(f)

    if content_file.exists():
        with open(content_file, 'r') as f:
            content = f.read()

    # Generate mint metadata
    mint_metadata = {
        "name": drop_id.replace('_', ' ').title(),
        "description": f"A drop in the XO universe - {drop_id}",
        "image": f"ipfs://Qm{hashlib.sha256(drop_id.encode()).hexdigest()[:44]}",
        "external_url": f"https://xo-vault.com/drops/{drop_id}",
        "attributes": []
    }

    # Add trait attributes
    for trait_name, trait_info in traits.items():
        if isinstance(trait_info, dict):
            mint_metadata["attributes"].append({
                "trait_type": "Trait",
                "value": trait_name,
                "rarity": trait_info.get("rarity", "common")
            })

            # Add game effects as attributes
            if "game_effects" in trait_info:
                for game, effects in trait_info["game_effects"].items():
                    for effect, value in effects.items():
                        mint_metadata["attributes"].append({
                            "trait_type": f"{game.title()} Effect",
                            "value": f"{effect}: {value}"
                        })

    # Save mint metadata
    metadata_file = bundle_dir / "mint.metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(mint_metadata, f, indent=2)

    # Generate unlockable content
    unlockable_dir = bundle_dir / "unlockable"
    unlockable_dir.mkdir(parents=True, exist_ok=True)

    unlockable_content = f"""# 🔓 Unlockable Content: {drop_id}

## 📜 Hidden Scrolls

This drop contains hidden scrolls and lore that are revealed to holders.

### 🧬 Trait Details

{chr(10).join([f'**{name}**: {info.get("description", "No description")} (Rarity: {info.get("rarity", "common")})' for name, info in traits.items() if isinstance(info, dict)])}

### 🎮 Game Compatibility

This drop's traits are compatible with:
- MarioKart: Speed and power effects
- Sims: Personality and skill enhancements
- Minecraft: Resource gathering and exploration bonuses

### 🌌 Lore Connection

{content}

---

*Unlockable content for {drop_id} holders*
*Part of the XO universe*"""

    unlockable_file = unlockable_dir / "scrolls.md"
    with open(unlockable_file, 'w') as f:
        f.write(unlockable_content)

    # Generate persona fusion
    persona_file = bundle_dir / "persona.json"
    persona_data = {
        "drop_id": drop_id,
        "persona_name": f"{drop_id}_holder",
        "description": f"Persona for {drop_id} holders",
        "traits": list(traits.keys()),
        "personality": "Holder of cosmic knowledge and power",
        "special_abilities": [
            "Access to hidden lore",
            "Cross-game trait compatibility",
            "Community voting rights",
            "Evolution pathway access"
        ],
        "created_at": datetime.now().isoformat()
    }

    with open(persona_file, 'w') as f:
        json.dump(persona_data, f, indent=2)

    # Generate QR landing page
    qr_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mint: {drop_id}</title>
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
        }}
        .mint-button {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border: none;
            color: white;
            padding: 20px 40px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 600;
            cursor: pointer;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 Mint {drop_id.replace('_', ' ').title()}</h1>
        <p>Join the XO universe and own this drop</p>
        <button class="mint-button" onclick="mint()">Mint Now</button>
        <p>Price: 0.021 ETH</p>
    </div>
    <script>
        function mint() {{
            window.location.href = '/mint/{drop_id}';
        }}
    </script>
</body>
</html>"""

    qr_file = bundle_dir / "qr_landing.html"
    with open(qr_file, 'w') as f:
        f.write(qr_html)

    # Create bundle manifest
    manifest = {
        "drop_id": drop_id,
        "template": template,
        "bundled_at": datetime.now().isoformat(),
        "files": {
            "mint_metadata": "mint.metadata.json",
            "unlockable_content": "unlockable/scrolls.md",
            "persona": "persona.json",
            "qr_landing": "qr_landing.html"
        },
        "traits_count": len(traits),
        "rarity_distribution": {
            trait_info.get("rarity", "common"): sum(1 for t in traits.values() if isinstance(t, dict) and t.get("rarity") == trait_info.get("rarity"))
            for trait_info in traits.values() if isinstance(trait_info, dict)
        }
    }

    manifest_file = bundle_dir / "bundle.manifest.yml"
    with open(manifest_file, 'w') as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Bundled {drop_id} for minting")
    print(f"📁 Bundle location: {bundle_dir}")
    print(f"📊 Traits: {len(traits)}")
    print(f"🎫 Ready for contract deployment")

    return True


@task
def deploy_with_dns(c, domains="xo-vault.com,xoseals.com,xoledger.com"):
    """
    Deploy with DNS configuration for multiple domains.

    Args:
        domains: Comma-separated list of domains
    """
    print(f"🌐 Deploying with DNS for domains: {domains}")

    # Create DNS configuration
    dns_dir = Path("deploy/dns")
    dns_dir.mkdir(parents=True, exist_ok=True)

    domains_list = [d.strip() for d in domains.split(",")]

    # Generate Cloudflare Pages configuration
    pages_config = {
        "name": "xo-universe",
        "production_branch": "main",
        "build_command": "npm run build",
        "output_directory": "public",
        "routes": []
    }

    # Add routes for each domain
    for domain in domains_list:
        pages_config["routes"].extend([
            {
                "source": f"https://{domain}/drops/*",
                "destination": "/drops/[drop_id]"
            },
            {
                "source": f"https://{domain}/constellation",
                "destination": "/constellation"
            },
            {
                "source": f"https://{domain}/vault/daily/*",
                "destination": "/vault/daily/[date]"
            }
        ])

    # Save Cloudflare configuration
    cf_config_file = dns_dir / "cloudflare-pages.json"
    with open(cf_config_file, 'w') as f:
        json.dump(pages_config, f, indent=2)

    # Generate redirect rules
    redirect_rules = []
    for domain in domains_list:
        redirect_rules.append({
            "domain": domain,
            "rules": [
                {
                    "source": "/drops/*",
                    "destination": "/drops/[drop_id]",
                    "status": 200
                },
                {
                    "source": "/constellation",
                    "destination": "/constellation/index.html",
                    "status": 200
                },
                {
                    "source": "/vault/daily/*",
                    "destination": "/vault/daily/[date].html",
                    "status": 200
                }
            ]
        })

    redirect_file = dns_dir / "redirect-rules.yml"
    with open(redirect_file, 'w') as f:
        yaml.dump(redirect_rules, f, default_flow_style=False, sort_keys=False)

    print(f"✅ DNS configuration generated")
    print(f"📁 Configuration files: {dns_dir}")
    print(f"🌐 Domains configured: {', '.join(domains_list)}")

    return True


# Create agent namespace
ns = Collection("agent")
ns.add_task(cosmic, "cosmic")
ns.add_task(explore, "explore")
ns.add_task(dispatch, "dispatch")
ns.add_task(trait_bridge, "trait-bridge")
ns.add_task(generate_prompts, "generate-prompts")
ns.add_task(dreamify, "dreamify")
ns.add_task(broadcast, "broadcast")
ns.add_task(initiate, "initiate")
ns.add_task(persona_craft, "persona-craft")
ns.add_task(constellation_link, "constellation-link")
ns.add_task(drop_regen, "drop-regen")
ns.add_task(vault_showcase, "vault-showcase")
ns.add_task(react, "react")
ns.add_task(morph, "morph")
ns.add_task(autopilot, "autopilot")
ns.add_task(portal, "portal")
ns.add_task(enable_enhancements, "enable-enhancements")
ns.add_task(constellation_feed, "constellation-feed")
ns.add_task(pulse_new, "pulse-new")
ns.add_task(pulse_sync, "pulse-sync")
ns.add_task(deploy_drop_url, "deploy-drop-url")
ns.add_task(drop_bundle, "drop-bundle")
ns.add_task(deploy_with_dns, "deploy-with-dns")
