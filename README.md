# Tiny Top‑Down Adventure (Raspberry Pi / Pygame)

A lightweight, NES‑style top‑down adventure game engine written for old Raspberry Pi (Raspbian Wheezy) and Pygame 1.9.x.  
It avoids external assets and draws everything procedurally, so you can just run it.

> ⚠️ **No Nintendo IP**: This is an original engine inspired by classic room‑scrolling games. No copyrighted names, maps, or sprites are included.

## Requirements

- Raspberry Pi running Raspbian Wheezy (or newer).
- Python 2.7 **or** Python 3.x. (Works on both; Python 2.7 + Pygame 1.9.1 was common on Wheezy.)
- Pygame 1.9.x (or newer):
  ```bash
  # Python 2.7 (typical Wheezy)
  sudo apt-get update
  sudo apt-get install python-pygame

  # Or for Python 3 if available on your system
  sudo apt-get install python3-pygame
  ```

## Run

From this folder:
```bash
# Python 2.7
python main.py

# or Python 3
python3 main.py
```

Controls (keyboard):
- Arrow keys: Move
- Z: Melee slash
- X: Use item (boomerang)
- Enter: Pause menu (shows stats), Escape: Quit

Performance tips on old Pi:
- In `settings.py`, lower `FPS` to 30, set `SCALE=2`, and keep windowed mode.
- Use the `--no-audio` flag if mixer initialization causes issues:
  ```bash
  python main.py --no-audio
  ```

## Project Layout

```
zelda_like_pi/
├── main.py            # Entry point / Game loop
├── settings.py        # Screen, colors, constants
├── world.py           # Rooms, tile map, transitions
├── tilemap.py         # Tile definitions & utilities
├── sprites.py         # Player, enemies, items
├── hud.py             # HUD (hearts, rupees)
├── utils.py           # Helpers (rect collisions, timing)
└── README.md
```

## Notes

- Room‑based scrolling (screen‑by‑screen) like early console adventure games.
- 16x16 tiles, base resolution 256x240; scaled up for modern screens via `SCALE`.
- Simple combat, enemies with basic AI, keys/doors, and a boomerang.
- Everything drawn with Pygame primitives to avoid external assets.

Have fun hacking on it—add new enemies, items, shops, dungeons, and puzzles!
