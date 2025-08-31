from __future__ import division
import pygame
from settings import TILE, C_GRASS, C_TREE, C_WALL, C_WATER, C_SAND, C_DOOR, C_LOCK

# Tile IDs
T_GRASS, T_TREE, T_WALL, T_WATER, T_SAND, T_DOOR, T_LOCK = range(7)

TILE_SOLID = {
    T_GRASS: False,
    T_TREE: True,
    T_WALL: True,
    T_WATER: True,
    T_SAND: False,
    T_DOOR: False,
    T_LOCK: True,    # locked until player has a key
}

TILE_COLOR = {
    T_GRASS: C_GRASS,
    T_TREE: C_TREE,
    T_WALL: C_WALL,
    T_WATER: C_WATER,
    T_SAND: C_SAND,
    T_DOOR: C_DOOR,
    T_LOCK: C_LOCK,
}

def draw_tile(surf, tid, x, y):
    color = TILE_COLOR.get(tid, (255,0,255))
    r = pygame.Rect(x, y, TILE, TILE)
    pygame.draw.rect(surf, color, r)
    # add simple accents
    if tid == T_GRASS:
        pygame.draw.line(surf, (72, 176, 72), (x+3, y+12), (x+8, y+12))
        pygame.draw.line(surf, (72, 176, 72), (x+10, y+6), (x+13, y+6))
    elif tid == T_TREE:
        pygame.draw.rect(surf, (16, 64, 16), r, 2)
    elif tid == T_WALL:
        pygame.draw.rect(surf, (96, 96, 112), r, 2)
    elif tid == T_WATER:
        pygame.draw.line(surf, (48, 128, 200), (x+2, y+12), (x+14, y+12))
        pygame.draw.line(surf, (48, 128, 200), (x+0, y+6), (x+10, y+6))
    elif tid == T_SAND:
        pygame.draw.line(surf, (220, 200, 130), (x+2, y+10), (x+9, y+10))
    elif tid == T_DOOR:
        pygame.draw.rect(surf, (100, 70, 30), r.inflate(-6, -4))
    elif tid == T_LOCK:
        pygame.draw.rect(surf, (100, 70, 30), r.inflate(-6, -4))
        pygame.draw.circle(surf, (50, 50, 50), (x+TILE//2, y+TILE//2), 3)

def room_solid_rects(room_grid, lock_open=False):
    solids = []
    h = len(room_grid)
    w = len(room_grid[0]) if h else 0
    for j in range(h):
        for i in range(w):
            tid = room_grid[j][i]
            solid = TILE_SOLID.get(tid, True)
            if tid == T_LOCK and lock_open:
                solid = False
            if solid:
                solids.append(pygame.Rect(i*TILE, j*TILE, TILE, TILE))
    return solids
