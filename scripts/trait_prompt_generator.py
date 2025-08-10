#!/usr/bin/env python3
"""
Trait Prompt Generator for GPT-5
Generates seed prompt templates based on trait characteristics and game compatibility.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_trait_data(drop_id: str) -> Dict[str, Any]:
    """Load trait data from a drop's .traits.yml file."""
    drop_paths = [
        Path("drops") / drop_id,
        Path("drops/drafts") / drop_id,
        Path("drops/sealed") / drop_id,
        Path("vault/drops") / drop_id,
    ]

    for path in drop_paths:
        traits_file = path / "hidden" / ".traits.yml"
        if traits_file.exists():
            with open(traits_file, 'r') as f:
                return yaml.safe_load(f)

    return {}


def generate_trait_prompts(trait_data: Dict[str, Any], drop_id: str) -> List[Dict[str, str]]:
    """Generate GPT-5 prompt templates for each trait."""
    prompts = []

    for trait_name, trait_info in trait_data.items():
        if isinstance(trait_info, dict):
            # Generate creative prompt
            creative_prompt = f"""You are analyzing the trait '{trait_name}' from the XO drop '{drop_id}'.

Trait Details:
- Name: {trait_name}
- Description: {trait_info.get('description', 'No description available')}
- Rarity: {trait_info.get('rarity', 'common')}
- Game Effects: {trait_info.get('game_effects', {})}

Generate 3 creative variations of this trait that could:
1. Enhance the original concept
2. Create an opposite/contrasting version
3. Evolve it into a more powerful form

For each variation, provide:
- Name
- Description
- Rarity level
- Game effects for MarioKart and Sims
- Lore connection to the original

Format your response as a structured list with clear sections."""

            # Generate lore expansion prompt
            lore_prompt = f"""Based on the trait '{trait_name}' from '{drop_id}', expand the universe lore.

Current trait context:
- Description: {trait_info.get('description', 'No description available')}
- Rarity: {trait_info.get('rarity', 'common')}
- Game compatibility: {trait_info.get('game_effects', {})}

Create:
1. A backstory explaining how this trait came to exist
2. 2-3 related characters or entities that might possess similar traits
3. A prophecy or legend involving this trait
4. How this trait connects to other drops in the XO universe

Make it engaging and interconnected with the broader XO mythology."""

            # Generate community engagement prompt
            community_prompt = f"""Create an engaging community prompt for the trait '{trait_name}' from '{drop_id}'.

Trait context:
- Description: {trait_info.get('description', 'No description available')}
- Rarity: {trait_info.get('rarity', 'common')}

Design a prompt that:
1. Invites community members to share their interpretation
2. Asks for creative ideas about how this trait might manifest
3. Encourages storytelling without requiring ownership
4. Connects to broader themes of creativity and imagination

Make it accessible to both casual fans and deep lore enthusiasts."""

            prompts.append({
                "trait_name": trait_name,
                "creative_variation": creative_prompt,
                "lore_expansion": lore_prompt,
                "community_engagement": community_prompt,
                "generated_at": datetime.now().isoformat()
            })

    return prompts


def save_prompts(prompts: List[Dict[str, str]], drop_id: str):
    """Save generated prompts to a file."""
    output_dir = Path("drops") / drop_id / "prompts"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "gpt5_trait_prompts.yml"

    with open(output_file, 'w') as f:
        yaml.dump({
            "drop_id": drop_id,
            "generated_at": datetime.now().isoformat(),
            "prompts": prompts
        }, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Saved {len(prompts)} trait prompts to: {output_file}")

    # Also create individual prompt files for easy use
    for prompt_data in prompts:
        trait_name = prompt_data["trait_name"]

        # Creative variation file
        creative_file = output_dir / f"{trait_name}_creative_variation.txt"
        with open(creative_file, 'w') as f:
            f.write(prompt_data["creative_variation"])

        # Lore expansion file
        lore_file = output_dir / f"{trait_name}_lore_expansion.txt"
        with open(lore_file, 'w') as f:
            f.write(prompt_data["lore_expansion"])

        # Community engagement file
        community_file = output_dir / f"{trait_name}_community_engagement.txt"
        with open(community_file, 'w') as f:
            f.write(prompt_data["community_engagement"])

    print(f"✅ Created individual prompt files for each trait")


def main():
    """Main function to generate trait prompts."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python trait_prompt_generator.py <drop_id>")
        print("Example: python trait_prompt_generator.py message_bottle")
        return

    drop_id = sys.argv[1]
    print(f"🎯 Generating GPT-5 trait prompts for: {drop_id}")

    # Load trait data
    trait_data = load_trait_data(drop_id)
    if not trait_data:
        print(f"❌ No trait data found for drop: {drop_id}")
        return

    print(f"📊 Found {len(trait_data)} traits to process")

    # Generate prompts
    prompts = generate_trait_prompts(trait_data, drop_id)

    # Save prompts
    save_prompts(prompts, drop_id)

    print(f"\n🎉 Successfully generated {len(prompts)} trait prompt sets!")
    print(f"📁 Check the 'drops/{drop_id}/prompts/' directory for the generated files.")


if __name__ == "__main__":
    main()
