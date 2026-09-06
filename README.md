# Tiny Top-Down Adventure — Modern Refresh

A lightweight, procedural, NES-inspired top-down adventure for Raspberry Pi / Pygame. It keeps the original project's 256×240 logical resolution and external-asset-free approach, but upgrades the character art, enemies, environment tiles, combat feel, room logic, and world layout.

The hero and creatures are **original procedural pixel art inspired by the visual language of early 8-bit adventure games**; this project does not ship Nintendo artwork or copied sprites.

## What's new

- A recognizable 16×16 pixel hero instead of a colored square: cap, face, tunic, belt, boots, shield, directional poses, and a two-frame walk animation.
- More detailed procedural enemies with distinct silhouettes and hit flashing.
- Richer grass, trees, bushes, rocks, water, sand, stone walls, doors, and locks.
- Fixed room transitions so the player cannot enter missing rooms.
- A connected seven-room overworld with a key-gated hidden shrine.
- Correct one-hit-per-sword-swing behavior instead of damaging on every overlapping frame.
- Diagonal movement normalization.
- Enemy chase/wander behavior, knockback, stun, and simple drops.
- Boomerang now stuns enemies and returns to the player rather than instantly deleting them.
- Heart pickups, room-clear rewards, improved HUD, room-name banners, pause screen, and game-over/restart flow.
- `--scale N` command-line option for modern displays while retaining integer pixel scaling.
- Still uses only Pygame primitives — no image files are required.

## Requirements

- Python 2.7 or Python 3.x
- Pygame 1.9.x or newer

This intentionally avoids f-strings, dataclasses, type annotations, NumPy, and external assets so it remains suitable for older Raspberry Pi installations.

## Run

```bash
python main.py
# or
python3 main.py
```

For an older Pi:

```bash
python main.py --no-audio --scale 2
```

## Controls

- Arrow keys — move
- Z or Left Ctrl — sword
- X or Left Alt — boomerang
- Enter — pause / resume
- R — restart after game over
- Escape — quit

## Project layout

```text
main.py       game loop, transitions, state, pickups, restart
settings.py   resolution, tuning, palette
world.py      room layouts, exits, locked door, pickups
tilemap.py    procedural terrain pixel art and collision
sprites.py    hero, enemies, sword, boomerang, combat
hud.py        hearts and inventory strip
utils.py      small helpers and frame timers
```

## Design goal

The refresh is deliberately closer to an early-console adventure game than to a modern high-resolution RPG: low logical resolution, hard pixel edges, limited colors, readable silhouettes, simple room-to-room exploration, and very low CPU/GPU requirements.
