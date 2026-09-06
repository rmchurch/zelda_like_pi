from __future__ import division
import pygame
from settings import (
    TILE, C_GRASS, C_GRASS_DARK, C_GRASS_LIGHT,
    C_TREE, C_TREE_DARK, C_TREE_LIGHT,
    C_WALL, C_WALL_DARK, C_WATER, C_WATER_LIGHT,
    C_SAND, C_SAND_DARK, C_DOOR, C_LOCK, C_ROCK, C_BUSH
)

# Tile IDs
T_GRASS, T_TREE, T_WALL, T_WATER, T_SAND, T_DOOR, T_LOCK, T_ROCK, T_BUSH = range(9)

TILE_SOLID = {
    T_GRASS: False,
    T_TREE: True,
    T_WALL: True,
    T_WATER: True,
    T_SAND: False,
    T_DOOR: False,
    T_LOCK: True,
    T_ROCK: True,
    T_BUSH: True,
}


def _px(surf, color, x, y, w=2, h=2):
    pygame.draw.rect(surf, color, (int(x), int(y), int(w), int(h)))


def draw_tile(surf, tid, x, y, phase=0):
    """Draw a 16x16 procedural pixel tile with no external artwork."""
    r = pygame.Rect(x, y, TILE, TILE)

    if tid == T_GRASS:
        pygame.draw.rect(surf, C_GRASS, r)
        seed = ((x // TILE) * 7 + (y // TILE) * 11) % 5
        if seed in (0, 2, 4):
            _px(surf, C_GRASS_DARK, x + 3, y + 11, 2, 3)
            _px(surf, C_GRASS_LIGHT, x + 5, y + 9, 1, 2)
        if seed in (1, 3):
            _px(surf, C_GRASS_DARK, x + 11, y + 5, 2, 2)
            _px(surf, C_GRASS_LIGHT, x + 8, y + 6, 2, 1)

    elif tid == T_TREE:
        pygame.draw.rect(surf, C_GRASS_DARK, r)
        # trunk under a chunky three-tone canopy
        _px(surf, (105, 66, 31), x + 6, y + 10, 4, 6)
        pygame.draw.rect(surf, C_TREE_DARK, (x + 1, y + 1, 14, 11))
        pygame.draw.rect(surf, C_TREE, (x + 3, y, 10, 13))
        _px(surf, C_TREE_LIGHT, x + 4, y + 2, 4, 3)
        _px(surf, C_TREE_LIGHT, x + 9, y + 6, 3, 3)
        _px(surf, C_TREE_DARK, x + 2, y + 8, 4, 3)

    elif tid == T_BUSH:
        pygame.draw.rect(surf, C_GRASS, r)
        pygame.draw.rect(surf, C_TREE_DARK, (x + 2, y + 4, 12, 9))
        pygame.draw.rect(surf, C_BUSH, (x + 3, y + 2, 10, 11))
        _px(surf, C_TREE_LIGHT, x + 5, y + 4, 3, 3)
        _px(surf, C_TREE_LIGHT, x + 10, y + 7, 2, 2)
        _px(surf, C_TREE_DARK, x + 7, y + 10, 3, 3)

    elif tid == T_WALL:
        pygame.draw.rect(surf, C_WALL, r)
        pygame.draw.line(surf, C_WALL_DARK, (x, y + 7), (x + 15, y + 7))
        pygame.draw.line(surf, C_WALL_DARK, (x, y + 15), (x + 15, y + 15))
        off = 0 if ((y // TILE) % 2 == 0) else 4
        for bx in range(-off, 16, 8):
            pygame.draw.line(surf, C_WALL_DARK, (x + bx, y), (x + bx, y + 7))
        for bx in range(off, 16, 8):
            pygame.draw.line(surf, C_WALL_DARK, (x + bx, y + 8), (x + bx, y + 15))
        pygame.draw.line(surf, (156, 150, 156), (x + 1, y + 1), (x + 14, y + 1))

    elif tid == T_ROCK:
        pygame.draw.rect(surf, C_GRASS, r)
        pygame.draw.polygon(surf, C_WALL_DARK, [
            (x + 3, y + 12), (x + 2, y + 7), (x + 5, y + 3),
            (x + 11, y + 2), (x + 14, y + 6), (x + 13, y + 12)
        ])
        pygame.draw.polygon(surf, C_ROCK, [
            (x + 4, y + 11), (x + 4, y + 7), (x + 6, y + 4),
            (x + 10, y + 4), (x + 12, y + 7), (x + 11, y + 11)
        ])
        _px(surf, (154, 150, 140), x + 6, y + 5, 4, 2)

    elif tid == T_WATER:
        pygame.draw.rect(surf, C_WATER, r)
        wave = 1 if (phase % 2) else 0
        pygame.draw.line(surf, C_WATER_LIGHT,
                         (x + 1 + wave, y + 5), (x + 8 + wave, y + 5))
        pygame.draw.line(surf, C_WATER_LIGHT,
                         (x + 8 - wave, y + 11), (x + 15 - wave, y + 11))
        _px(surf, (28, 74, 142), x + 3, y + 13, 5, 1)

    elif tid == T_SAND:
        pygame.draw.rect(surf, C_SAND, r)
        _px(surf, C_SAND_DARK, x + 4, y + 5, 1, 1)
        _px(surf, C_SAND_DARK, x + 11, y + 10, 2, 1)
        _px(surf, (230, 208, 142), x + 7, y + 13, 2, 1)

    elif tid in (T_DOOR, T_LOCK):
        # stone/wood doorway cut into the room border
        pygame.draw.rect(surf, C_WALL_DARK, r)
        pygame.draw.rect(surf, C_DOOR, (x + 3, y + 2, 10, 14))
        pygame.draw.rect(surf, (77, 48, 28), (x + 5, y + 4, 6, 12))
        if tid == T_DOOR:
            pygame.draw.rect(surf, (20, 20, 18), (x + 6, y + 5, 4, 11))
        else:
            pygame.draw.rect(surf, C_LOCK, (x + 6, y + 7, 4, 5))
            pygame.draw.rect(surf, C_LOCK, (x + 7, y + 5, 2, 3))
            _px(surf, (75, 60, 32), x + 7, y + 9, 1, 2)

    else:
        pygame.draw.rect(surf, (255, 0, 255), r)


def room_solid_rects(room_grid):
    solids = []
    h = len(room_grid)
    w = len(room_grid[0]) if h else 0
    for j in range(h):
        for i in range(w):
            tid = room_grid[j][i]
            if TILE_SOLID.get(tid, True):
                solids.append(pygame.Rect(i * TILE, j * TILE, TILE, TILE))
    return solids
