from __future__ import division

# ---------- Screen & Timing ----------
TILE = 16
ROOM_W, ROOM_H = 16, 15             # 256x240 logical resolution
BASE_W, BASE_H = ROOM_W*TILE, ROOM_H*TILE
SCALE = 3                           # crisp integer scale; use 2 on older displays
FPS = 60                            # use 30 on very old Raspberry Pi hardware

# ---------- Gameplay ----------
PLAYER_SPEED = 1.55                  # pixels/frame at 60 FPS
ENEMY_SPEED = 0.60
INVULN_TIME = 48                    # frames after taking damage
SLASH_TIME = 10
ATTACK_COOLDOWN = 8
ENEMY_HURT_TIME = 10
ENEMY_STUN_TIME = 28
BOOMERANG_SPEED = 3.0
BOOMERANG_RANGE = TILE * 6
ROOM_BANNER_TIME = 75

# ---------- NES-inspired palette ----------
BLACK = (8, 8, 8)
WHITE = (244, 244, 232)
UI_BG = (16, 16, 16)
UI_FG = (240, 232, 208)

# environment
C_GRASS = (82, 156, 74)
C_GRASS_DARK = (48, 112, 48)
C_GRASS_LIGHT = (112, 184, 88)
C_TREE = (30, 96, 42)
C_TREE_DARK = (18, 64, 30)
C_TREE_LIGHT = (54, 132, 54)
C_WALL = (122, 118, 126)
C_WALL_DARK = (82, 78, 92)
C_WATER = (42, 96, 168)
C_WATER_LIGHT = (72, 140, 204)
C_SAND = (210, 188, 120)
C_SAND_DARK = (178, 150, 88)
C_DOOR = (132, 82, 38)
C_LOCK = (218, 172, 52)
C_ROCK = (112, 112, 104)
C_BUSH = (42, 122, 48)

# hero
C_TUNIC = (62, 150, 58)
C_TUNIC_DARK = (34, 104, 38)
C_SKIN = (238, 184, 118)
C_HAIR = (116, 72, 36)
C_BOOT = (90, 52, 28)
C_BELT = (114, 72, 32)
C_SHIELD = (74, 94, 146)
C_SHIELD_TRIM = (218, 174, 54)
C_SWORD = (232, 232, 216)

# enemies / pickups
C_ENEMY1 = (190, 58, 48)
C_ENEMY2 = (208, 116, 42)
C_ENEMY_DARK = (92, 42, 32)
C_KEY = (246, 210, 72)
C_RUPEE = (34, 196, 176)
C_HEART = (232, 48, 48)

# wooden sword accents
C_WOOD_DARK = (102, 58, 28)
C_WOOD_LIGHT = (190, 124, 62)
C_GUARD_GOLD = (218, 165, 32)

# Kept for compatibility with older code / controller mappings
KEY_ATTACK = ' '
KEY_ITEM = 'f'
KEY_SPRINT = 'd'
