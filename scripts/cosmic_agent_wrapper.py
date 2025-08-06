#!/usr/bin/env python3
"""
🌌 XO Cosmic Agent Wrapper
AIO Creative Agent for Cursor/CLI - lore-driven, persona-aware, asset-tagging pipelines
Fully flavored for XO Drops, Vaults, Loreloops, and Cosmic Prompting

Usage:
    python scripts/cosmic_agent_wrapper.py message_bottle scroll_02 vault_keeper
    # Or via xo-fab agent.cosmic:message_bottle:scroll_02
"""

import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


def load_persona_prompt(persona: str = "vault_keeper") -> str:
    """Load persona prompts from persona library"""
    persona_map = {
        "vault_keeper": """
🧙‍♂️ You are the Vault Keeper, guardian of the XO verse's most precious lore.
Your voice is mystical yet grounded, weaving ancient wisdom with modern digital magic.
You see patterns across drops, connections between traits, and the deeper narrative threads.
You speak in measured tones, often using cosmic metaphors and references to scrolls, seals, and hidden knowledge.
        """.strip(),
        
        "lore_weaver": """
📜 You are the Lore Weaver, master storyteller of interconnected narratives.
You excel at finding hidden connections, creating engaging backstories, and expanding universe mythology.
Your tone is creative and immersive, always building upon existing elements to create richer worlds.
        """.strip(),
        
        "trait_alchemist": """
🧬 You are the Trait Alchemist, master of characteristics and evolutionary pathways.
You understand how traits combine, mutate, and influence external systems and games.
Your expertise lies in creating balanced, interesting, and game-compatible trait systems.
        """.strip(),
        
        "inbox_curator": """
📬 You are the Inbox Curator, facilitator of community engagement and conversations.
You create compelling prompts that invite participation without requiring ownership.
Your specialty is crafting accessible entry points into complex lore systems.
        """.strip()
    }
    
    return persona_map.get(persona, persona_map["vault_keeper"])


def load_drop_metadata(drop_id: str) -> Dict:
    """Load all available metadata for a drop"""
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id
    ]
    
    metadata = {"drop_id": drop_id, "found_path": None}
    
    for drop_path in drop_paths:
        if drop_path.exists():
            metadata["found_path"] = str(drop_path)
            
            # Load status file
            status_file = drop_path / f"{drop_id}.status.json"
            if status_file.exists():
                with open(status_file) as f:
                    metadata["status"] = json.load(f)
            
            # Load metadata file
            meta_file = drop_path / f"{drop_id}.meta.yml"
            if meta_file.exists():
                with open(meta_file) as f:
                    metadata["meta"] = yaml.safe_load(f)
            
            # Load traits file
            traits_file = drop_path / "hidden" / ".traits.yml"
            if traits_file.exists():
                with open(traits_file) as f:
                    metadata["traits"] = yaml.safe_load(f)
            
            # Load lore file
            lore_file = drop_path / ".lore.yml"
            if lore_file.exists():
                with open(lore_file) as f:
                    metadata["lore"] = yaml.safe_load(f)
            
            # Load content file
            content_file = drop_path / f"{drop_id}.mdx"
            if content_file.exists():
                with open(content_file) as f:
                    metadata["content"] = f.read()
            
            break
    
    return metadata


def generate_cosmic_prompt(drop_id: str, variant: str, persona: str = "vault_keeper") -> str:
    """
    Generates a creative, narrative-rich prompt for use in image/video/text generation.
    Adjusts for lore, traits, and context from XO drop folders.
    """
    
    # Load components
    persona_prompt = load_persona_prompt(persona)
    metadata = load_drop_metadata(drop_id)
    
    prompt_parts = []
    
    # 1. Add core persona prompt
    prompt_parts.append(f"🧙‍♂️ **Persona Context:**\n{persona_prompt}")
    
    # 2. Add drop metadata
    if metadata.get("status"):
        status = metadata["status"]
        title = status.get("title", drop_id)
        tags = ", ".join(status.get("tags", []))
        prompt_parts.append(f"📦 **Drop Context:** {title}\n🏷️ **Tags:** {tags}")
    
    if metadata.get("meta"):
        meta = metadata["meta"]
        if "description" in meta:
            prompt_parts.append(f"📄 **Description:** {meta['description']}")
    
    # 3. Add trait context if present
    if metadata.get("traits"):
        traits_text = yaml.dump(metadata["traits"], default_flow_style=False)
        prompt_parts.append(f"🧩 **Current Traits:**\n```yaml\n{traits_text}```")
    
    # 4. Add existing lore
    if metadata.get("lore"):
        lore_text = yaml.dump(metadata["lore"], default_flow_style=False)
        prompt_parts.append(f"📜 **Existing Lore:**\n```yaml\n{lore_text}```")
    
    # 5. Add content preview
    if metadata.get("content"):
        content_preview = metadata["content"][:300] + "..." if len(metadata["content"]) > 300 else metadata["content"]
        prompt_parts.append(f"📝 **Content Preview:**\n{content_preview}")
    
    # 6. Add specific variant target
    prompt_parts.append(f"🎨 **Variant Target:** {variant}")
    
    # 7. Add creative directive
    creative_directive = """
✨ **Creative Prompt Goal:** 
Extend the visual or narrative theme with new scrolls, traits, messages, or game-compatible evolutions.
Consider how this variant connects to the existing lore while adding fresh possibilities.
Think about cross-game compatibility (MarioKart speed boosts, Sims creativity traits, etc.).
"""
    prompt_parts.append(creative_directive.strip())
    
    return "\n\n".join(prompt_parts)


def suggest_trait_variants(drop_id: str, count: int = 3) -> List[Dict]:
    """Generate trait variant suggestions in .traits.yml format"""
    metadata = load_drop_metadata(drop_id)
    
    base_traits = metadata.get("traits", {})
    suggestions = []
    
    variant_templates = [
        {
            "name": f"evolved_{drop_id}",
            "description": "Enhanced version with amplified core characteristics",
            "rarity": "rare",
            "game_effects": {
                "mario_kart": "speed_boost_15",
                "sims": "creativity_plus_2"
            }
        },
        {
            "name": f"shadow_{drop_id}",
            "description": "Mysterious variant with hidden depths",
            "rarity": "epic", 
            "game_effects": {
                "mario_kart": "stealth_mode",
                "sims": "charisma_plus_3"
            }
        },
        {
            "name": f"cosmic_{drop_id}",
            "description": "Transcendent form connected to the greater universe",
            "rarity": "legendary",
            "game_effects": {
                "mario_kart": "anti_gravity",
                "sims": "inspiration_aura"
            }
        }
    ]
    
    return variant_templates[:count]


def generate_inbox_seed(drop_id: str, persona: str = "inbox_curator") -> str:
    """Generate inbox seed content for community engagement"""
    metadata = load_drop_metadata(drop_id)
    persona_prompt = load_persona_prompt(persona)
    
    title = metadata.get("status", {}).get("title", drop_id)
    
    seed_template = f"""
# 📬 Community Inbox: {title}

{persona_prompt}

## 🎯 Engagement Prompt

*Based on the lore and traits of {title}, what story would you add to this universe?*

### Conversation Starters:
- What do you think happened before this moment?
- How might this trait manifest in different worlds?
- What questions would you ask the creator?

### Guidelines:
- No ownership required - all perspectives welcome
- Build upon existing lore respectfully  
- Consider cross-universe connections
- Keep it creative and constructive

---
*Generated by XO Cosmic Agent - {datetime.now().isoformat()}*
"""
    
    return seed_template.strip()


def main():
    """CLI interface for cosmic agent wrapper"""
    if len(sys.argv) < 3:
        print("Usage: python cosmic_agent_wrapper.py <drop_id> <variant> [persona]")
        print("Example: python cosmic_agent_wrapper.py message_bottle scroll_02 vault_keeper")
        sys.exit(1)
    
    drop_id = sys.argv[1]
    variant = sys.argv[2]
    persona = sys.argv[3] if len(sys.argv) > 3 else "vault_keeper"
    
    print("🌌 XO Cosmic Agent Wrapper")
    print("=" * 50)
    
    # Generate cosmic prompt
    cosmic_prompt = generate_cosmic_prompt(drop_id, variant, persona)
    print("\n🎨 **COSMIC PROMPT:**")
    print(cosmic_prompt)
    
    # Generate trait suggestions
    print("\n\n🧬 **TRAIT VARIANT SUGGESTIONS:**")
    variants = suggest_trait_variants(drop_id)
    for i, variant_data in enumerate(variants, 1):
        print(f"\n{i}. **{variant_data['name']}**")
        print(f"   Description: {variant_data['description']}")
        print(f"   Rarity: {variant_data['rarity']}")
        print(f"   Game Effects: {variant_data['game_effects']}")
    
    # Generate inbox seed
    print("\n\n📬 **INBOX SEED:**")
    inbox_seed = generate_inbox_seed(drop_id, "inbox_curator")
    print(inbox_seed)


if __name__ == "__main__":
    main()