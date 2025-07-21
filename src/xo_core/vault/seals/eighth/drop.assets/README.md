# Drop Assets for Eighth Seal

This folder contains the visual assets related to the "Eighth Seal – Scroll Bearer" NFT drop.

## Folder Structure

- `original/`: High-resolution original artwork (e.g. full-size PNG from MidJourney or other source)
- `webp/`: Optimized images for preview and metadata
  - `scroll-optimized.webp`: Web-friendly version used in `000.json`
  - `scroll-thumbnail.webp`: Small version for galleries
- `midjourney/`: Raw output images from MidJourney or prompt sources

## Usage Notes

- Always pin updated images to IPFS before referencing them in metadata or preview files.
- Update `000.json` → `"image": "ipfs://<CID>/scroll-optimized.webp"`
- Update `_drop.yml` → `cid` to match new upload
- Archive full-size originals in `original/` for reference or future use.

## Versioning

Keep filenames consistent across edits. Use `scroll-optimized.webp` and `scroll-thumbnail.webp` as standard names unless intentionally versioned.

## Prompt Suggestions

> "Ancient parchment scroll with gold-tipped ends, floating mid-air, tribal energy, light fog, divine presence --v 6 --ar 2:3 --style raw"

---

Maintained by XO Vault Drop System
