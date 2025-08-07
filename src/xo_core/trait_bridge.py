"""
XO Trait Bridge System
Defines external behavior for traits across different games and platforms.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GameEffect:
    """Represents a game effect for a trait."""
    game: str
    effect_type: str
    value: Any
    description: str
    rarity_multiplier: float = 1.0


@dataclass
class TraitBridge:
    """Represents a trait's bridge to external systems."""
    trait_name: str
    drop_id: str
    base_rarity: str
    game_effects: List[GameEffect]
    cross_platform_sync: bool = True
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class TraitBridgeManager:
    """Manages trait bridges across different games and platforms."""
    
    def __init__(self, base_path: str = "drops"):
        self.base_path = Path(base_path)
        self.supported_games = {
            "mario_kart": {
                "speed_boost": {"min": 0.1, "max": 0.5, "unit": "multiplier"},
                "stealth_mode": {"duration": 30, "unit": "seconds"},
                "anti_gravity": {"height": 2.0, "unit": "meters"},
                "shield_boost": {"duration": 15, "unit": "seconds"}
            },
            "sims": {
                "creativity_plus": {"min": 1, "max": 5, "unit": "points"},
                "charisma_plus": {"min": 1, "max": 3, "unit": "points"},
                "inspiration_aura": {"radius": 10, "unit": "meters"},
                "skill_boost": {"skill": "random", "multiplier": 1.5}
            },
            "minecraft": {
                "mining_speed": {"multiplier": 1.2, "unit": "speed"},
                "jump_boost": {"height": 1.5, "unit": "blocks"},
                "night_vision": {"duration": 300, "unit": "seconds"},
                "resource_finder": {"radius": 50, "unit": "blocks"}
            }
        }
    
    def create_bridge_from_trait(self, drop_id: str, trait_name: str, trait_data: Dict[str, Any]) -> TraitBridge:
        """Create a trait bridge from existing trait data."""
        game_effects = []
        
        # Extract game effects from trait data
        if "game_effects" in trait_data:
            for game, effects in trait_data["game_effects"].items():
                if isinstance(effects, dict):
                    for effect_type, value in effects.items():
                        game_effects.append(GameEffect(
                            game=game,
                            effect_type=effect_type,
                            value=value,
                            description=f"{effect_type} effect for {game}"
                        ))
        
        return TraitBridge(
            trait_name=trait_name,
            drop_id=drop_id,
            base_rarity=trait_data.get("rarity", "common"),
            game_effects=game_effects
        )
    
    def save_bridge(self, bridge: TraitBridge) -> bool:
        """Save a trait bridge to file."""
        try:
            bridge_dir = self.base_path / bridge.drop_id / "bridges"
            bridge_dir.mkdir(parents=True, exist_ok=True)
            
            bridge_file = bridge_dir / f"{bridge.trait_name}.bridge.yml"
            
            # Convert to dict for YAML serialization
            bridge_dict = asdict(bridge)
            
            with open(bridge_file, 'w') as f:
                yaml.dump(bridge_dict, f, default_flow_style=False, sort_keys=False)
            
            return True
        except Exception as e:
            print(f"❌ Failed to save bridge: {e}")
            return False
    
    def load_bridge(self, drop_id: str, trait_name: str) -> Optional[TraitBridge]:
        """Load a trait bridge from file."""
        try:
            bridge_file = self.base_path / drop_id / "bridges" / f"{trait_name}.bridge.yml"
            
            if not bridge_file.exists():
                return None
            
            with open(bridge_file, 'r') as f:
                bridge_data = yaml.safe_load(f)
            
            # Convert game_effects back to GameEffect objects
            game_effects = []
            for effect_data in bridge_data.get("game_effects", []):
                game_effects.append(GameEffect(**effect_data))
            
            bridge_data["game_effects"] = game_effects
            
            return TraitBridge(**bridge_data)
        except Exception as e:
            print(f"❌ Failed to load bridge: {e}")
            return None
    
    def generate_game_code(self, bridge: TraitBridge, game: str) -> str:
        """Generate code for a specific game implementation."""
        if game not in self.supported_games:
            return f"// Unsupported game: {game}"
        
        game_effects = [e for e in bridge.game_effects if e.game == game]
        
        if not game_effects:
            return f"// No effects defined for {game}"
        
        code_lines = [
            f"// XO Trait Bridge: {bridge.trait_name}",
            f"// Drop: {bridge.drop_id}",
            f"// Generated: {datetime.now().isoformat()}",
            "",
            f"class {bridge.trait_name.title().replace('_', '')}Trait:",
            "    def __init__(self):",
            f"        self.trait_name = '{bridge.trait_name}'",
            f"        self.rarity = '{bridge.base_rarity}'",
            "        self.effects = {}",
            ""
        ]
        
        for effect in game_effects:
            code_lines.extend([
                f"        # {effect.description}",
                f"        self.effects['{effect.effect_type}'] = {{",
                f"            'value': {effect.value},",
                f"            'description': '{effect.description}'",
                "        }",
                ""
            ])
        
        code_lines.extend([
            "    def apply_effects(self, player):",
            "        # Apply trait effects to player",
            "        for effect_type, effect_data in self.effects.items():",
            "            self._apply_effect(player, effect_type, effect_data)",
            "",
            "    def _apply_effect(self, player, effect_type, effect_data):",
            "        # Implementation specific to game",
            "        pass"
        ])
        
        return "\n".join(code_lines)
    
    def export_for_game(self, drop_id: str, game: str) -> Dict[str, Any]:
        """Export all trait bridges for a specific game."""
        bridges = []
        
        # Find all bridge files for the drop
        bridge_dir = self.base_path / drop_id / "bridges"
        if bridge_dir.exists():
            for bridge_file in bridge_dir.glob("*.bridge.yml"):
                trait_name = bridge_file.stem
                bridge = self.load_bridge(drop_id, trait_name)
                
                if bridge:
                    # Filter effects for the specific game
                    game_effects = [e for e in bridge.game_effects if e.game == game]
                    if game_effects:
                        bridges.append({
                            "trait_name": bridge.trait_name,
                            "rarity": bridge.base_rarity,
                            "effects": [asdict(e) for e in game_effects]
                        })
        
        return {
            "drop_id": drop_id,
            "game": game,
            "exported_at": datetime.now().isoformat(),
            "traits": bridges
        }


def create_bridge_from_traits(drop_id: str) -> bool:
    """Create bridges for all traits in a drop."""
    manager = TraitBridgeManager()
    
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
            with open(traits_file, 'r') as f:
                trait_data = yaml.safe_load(f)
            break
    
    if not trait_data:
        print(f"❌ No trait data found for drop: {drop_id}")
        return False
    
    created_count = 0
    for trait_name, trait_info in trait_data.items():
        if isinstance(trait_info, dict):
            bridge = manager.create_bridge_from_trait(drop_id, trait_name, trait_info)
            if manager.save_bridge(bridge):
                created_count += 1
                print(f"✅ Created bridge for trait: {trait_name}")
    
    print(f"🎉 Created {created_count} trait bridges for drop: {drop_id}")
    return True


def export_game_implementation(drop_id: str, game: str) -> bool:
    """Export trait bridges for a specific game implementation."""
    manager = TraitBridgeManager()
    
    # Export bridges for the game
    export_data = manager.export_for_game(drop_id, game)
    
    if not export_data["traits"]:
        print(f"❌ No trait bridges found for {drop_id} in {game}")
        return False
    
    # Save export
    export_dir = Path("drops") / drop_id / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    export_file = export_dir / f"{game}_traits.json"
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(export_data['traits'])} traits for {game}")
    print(f"📁 Export saved to: {export_file}")
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python trait_bridge.py <command> <drop_id> [game]")
        print("Commands:")
        print("  create <drop_id>     - Create bridges for all traits in a drop")
        print("  export <drop_id> <game> - Export bridges for a specific game")
        sys.exit(1)
    
    command = sys.argv[1]
    drop_id = sys.argv[2]
    
    if command == "create":
        create_bridge_from_traits(drop_id)
    elif command == "export":
        if len(sys.argv) < 4:
            print("❌ Game parameter required for export command")
            sys.exit(1)
        game = sys.argv[3]
        export_game_implementation(drop_id, game)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
