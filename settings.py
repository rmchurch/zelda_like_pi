from __future__ import division

# ---------- Screen & Timing ----------
TILE = 16
ROOM_W, ROOM_H = 16, 15             # 16x15 tiles => 256x240 like NES
BASE_W, BASE_H = ROOM_W*TILE, ROOM_H*TILE
SCALE = 2                           # 2x scale -> 512x480; use 3 on newer Pis
FPS = 60                            # set 30 on very old hardware

# ---------- Gameplay ----------
PLAYER_SPEED = 5                  # tiles per 10 frames approx
ENEMY_SPEED  = 4.5
INVULN_TIME  = 30                   # frames after taking hit
SLASH_TIME   = 8                    # frames
BOOMERANG_SPEED = 9.8

BOOMERANG_RANGE = TILE*6

# ---------- Colors (R,G,B) ----------
BLACK = (0,0,0)
WHITE = (255,255,255)
UI_BG = (24, 24, 24)
UI_FG = (240, 240, 240)

# tile colors
C_GRASS = (64, 160, 64)
C_TREE  = (24, 96, 24)
C_WALL  = (112, 112, 128)
C_WATER = (32, 96, 160)
C_SAND  = (210, 188, 120)
C_DOOR  = (150, 100, 40)
C_LOCK  = (190, 150, 80)

# player/enemy colors
C_PLAYER = (240, 216, 64)
C_SWORD  = (248, 248, 232)
C_ENEMY1 = (200, 64, 64)
C_ENEMY2 = (200, 120, 40)
C_KEY    = (255, 220, 90)
C_RUPEE  = (0, 180, 180)

# new sword colors
C_WOOD_DARK  = (139, 69, 19)   # grip (dark brown)
C_WOOD_LIGHT = (205, 133, 63)  # blade (lighter brown)
C_GUARD_GOLD = (218, 165, 32)  # cross-guard (gold-ish)

# Inputs
KEY_ATTACK = ' '
KEY_ITEM   = 'f'
KEY_SPRINT = 'd'
