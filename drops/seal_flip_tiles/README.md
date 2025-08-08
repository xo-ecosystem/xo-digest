# Seal Flip Roof Tiles — Drop Concept

A tile set inspired by the "flippers" ethos — find the hidden edge, flip the roof, reveal the seal. Each tile is a micro-provenance artifact with material, patina, and wear encoded as traits.

- Provenance: tiles originate from roof segments (ridge, eave, gable), carrying pitch and exposure.
- Game mapping: some tiles add `game_effects.unity_webgl.glow` to power the glow demo.
- Viewer: explore in `/traits`; a drop page can link to `/three-glow-demo`.

Schema fields used:
- id, name, type, file, rarity, title, media, tags, description
- attributes: material, patina, scratch_density, origin, roof_pitch
- optional game_effects.unity_webgl.glow

Preview quickstart:
- Start API: `uvicorn src.xo_core.api.vault_server:app --port 8000`
- Optional fallback: `python scripts/build_traits_index.py`
- Inspect: `curl -s http://localhost:8000/api/traits/seal_flip_tiles | jq`
- UI: open `/traits`; tiles with glow show a “Glow-Ready” demo link on a drop page.
