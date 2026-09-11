from __future__ import division
import pygame
from settings import TILE, ROOM_W, ROOM_H, C_KEY, C_RUPEE, C_HEART, C_GRASS_DARK
from tilemap import (
    draw_tile, room_solid_rects,
    T_GRASS, T_TREE, T_WALL, T_WATER, T_SAND, T_DOOR, T_LOCK, T_ROCK, T_BUSH
)

SIDE_TILE = {
    'N': (ROOM_W // 2, 0),
    'S': (ROOM_W // 2, ROOM_H - 1),
    'W': (0, ROOM_H // 2),
    'E': (ROOM_W - 1, ROOM_H // 2),
}


class Room(object):
    def __init__(self, name, grid, exits=None, pickups=None, enemy_specs=None):
        self.name = name
        self.grid = grid
        self.exits = exits or {}          # side -> destination (rx, ry)
        self.pickups = pickups or []
        self.enemy_specs = enemy_specs or []
        self.enemies = []
        self.spawned = False
        self.cleared_reward = False
        self._solid_cache = None
        self._background_cache = [None, None]
        self._has_animated_tiles = any(T_WATER in row for row in grid)

    def _invalidate_static_cache(self):
        self._solid_cache = None
        self._background_cache = [None, None]

    def _build_background(self, phase):
        bg = pygame.Surface((ROOM_W * TILE, ROOM_H * TILE))
        for j, row in enumerate(self.grid):
            for i, tid in enumerate(row):
                draw_tile(bg, tid, i * TILE, j * TILE, phase)
        # Matching the display pixel format makes repeated blits much cheaper
        # on old SDL/Pygame builds.  convert() is safe after set_mode().
        try:
            bg = bg.convert()
        except Exception:
            pass
        return bg

    def draw(self, surf, phase=0):
        # Almost the entire room is static.  Render it once and then blit one
        # cached 256x240 image per frame instead of reissuing hundreds of
        # pygame.draw calls.  Only water needs the second animation phase.
        idx = (phase & 1) if self._has_animated_tiles else 0
        bg = self._background_cache[idx]
        if bg is None:
            bg = self._build_background(idx)
            self._background_cache[idx] = bg
        surf.blit(bg, (0, 0))

    def solid_rects(self):
        if self._solid_cache is None:
            self._solid_cache = room_solid_rects(self.grid)
        return self._solid_cache

    def tile_for_side(self, side):
        i, j = SIDE_TILE[side]
        return self.grid[j][i]

    def unlock_near_player(self, player):
        if player.keys <= 0:
            return False
        probe = player.rect().inflate(8, 8)
        for side in self.exits:
            i, j = SIDE_TILE[side]
            if self.grid[j][i] != T_LOCK:
                continue
            lock_rect = pygame.Rect(i * TILE, j * TILE, TILE, TILE)
            if probe.colliderect(lock_rect):
                self.grid[j][i] = T_DOOR
                self._invalidate_static_cache()
                player.keys -= 1
                return True
        return False


def make_rect_pickup(i, j):
    return pygame.Rect(i * TILE + 4, j * TILE + 4, TILE - 8, TILE - 8)


def pickup(kind, i, j):
    return {'type': kind, 'rect': make_rect_pickup(i, j), 'alive': True}


def base_room(fill=T_GRASS):
    g = [[fill for _ in range(ROOM_W)] for __ in range(ROOM_H)]
    for i in range(ROOM_W):
        g[0][i] = T_WALL
        g[ROOM_H - 1][i] = T_WALL
    for j in range(ROOM_H):
        g[j][0] = T_WALL
        g[j][ROOM_W - 1] = T_WALL
    return g


def add_exit(g, side, locked=False):
    i, j = SIDE_TILE[side]
    g[j][i] = T_LOCK if locked else T_DOOR


def make_meadow():
    g = base_room()
    for i, j in [(3, 3), (12, 3), (3, 11), (12, 11)]:
        g[j][i] = T_TREE
    for i, j in [(5, 4), (10, 10), (4, 8), (11, 6)]:
        g[j][i] = T_BUSH
    g[5][7] = T_ROCK
    g[9][9] = T_ROCK
    add_exit(g, 'E')
    add_exit(g, 'S')
    return g


def make_forest():
    g = base_room()
    for j in range(2, ROOM_H - 2):
        for i in range(2, ROOM_W - 2):
            if ((i * 5 + j * 3) % 9 == 0) and not (6 <= i <= 10 and 5 <= j <= 9):
                g[j][i] = T_TREE
            elif ((i * 7 + j * 2) % 13 == 0):
                g[j][i] = T_BUSH
    add_exit(g, 'W')
    add_exit(g, 'E')
    add_exit(g, 'S')
    add_exit(g, 'N', locked=True)
    return g


def make_lake():
    g = base_room()
    for j in range(4, 11):
        for i in range(4, 12):
            g[j][i] = T_WATER
    for i in range(3, 13):
        g[3][i] = T_SAND
        g[11][i] = T_SAND
    for j in range(4, 11):
        g[j][3] = T_SAND
        g[j][12] = T_SAND
    # narrow sand causeway to a tiny island holding the key
    for i in range(3, 10):
        g[7][i] = T_SAND
    add_exit(g, 'N')
    add_exit(g, 'E')
    return g


def make_ruins():
    g = base_room()
    for i in range(3, 13):
        if i not in (7, 8):
            g[4][i] = T_WALL
            g[10][i] = T_WALL
    for j in range(5, 10):
        g[j][3] = T_WALL
        g[j][12] = T_WALL
    for i, j in [(5, 6), (10, 6), (5, 9), (10, 9)]:
        g[j][i] = T_ROCK
    add_exit(g, 'W')
    add_exit(g, 'N')
    add_exit(g, 'E')
    return g


def make_hill():
    g = base_room()
    for i, j in [(4, 3), (7, 2), (11, 4), (5, 10), (9, 11), (12, 8)]:
        g[j][i] = T_ROCK
    for i, j in [(3, 7), (7, 8), (10, 6), (12, 11)]:
        g[j][i] = T_BUSH
    add_exit(g, 'W')
    add_exit(g, 'S')
    return g


def make_grove():
    g = base_room()
    for i in range(2, 14, 2):
        g[3][i] = T_TREE
        g[11][i] = T_TREE
    for i in range(3, 13, 3):
        g[7][i] = T_BUSH
    add_exit(g, 'N')
    add_exit(g, 'W')
    return g


def make_sanctuary():
    g = base_room()
    for i in range(2, 14):
        g[3][i] = T_WALL
    g[3][7] = T_DOOR
    g[3][8] = T_DOOR
    for i, j in [(4, 7), (11, 7), (5, 10), (10, 10)]:
        g[j][i] = T_ROCK
    add_exit(g, 'S')
    return g


def build_world():
    rooms = {}

    rooms[(0, 0)] = Room(
        'Greenfield', make_meadow(),
        exits={'E': (1, 0), 'S': (0, 1)},
        pickups=[pickup('rupee', 2, 2)],
        enemy_specs=[(70, 100, 0), (180, 135, 1)]
    )

    rooms[(1, 0)] = Room(
        'Old Woods', make_forest(),
        exits={'W': (0, 0), 'E': (2, 0), 'S': (1, 1), 'N': (1, -1)},
        pickups=[pickup('rupee', 13, 11)],
        enemy_specs=[(78, 78, 0), (165, 70, 0), (130, 150, 1)]
    )

    rooms[(0, 1)] = Room(
        'Mirror Pond', make_lake(),
        exits={'N': (0, 0), 'E': (1, 1)},
        pickups=[pickup('key', 7, 7), pickup('rupee', 13, 2)],
        enemy_specs=[(45, 55, 0), (205, 170, 0)]
    )

    rooms[(1, 1)] = Room(
        'Broken Court', make_ruins(),
        exits={'W': (0, 1), 'N': (1, 0), 'E': (2, 1)},
        pickups=[pickup('heart', 8, 7)],
        enemy_specs=[(82, 116, 1), (172, 116, 1), (128, 170, 0)]
    )

    rooms[(2, 0)] = Room(
        'Stone Hill', make_hill(),
        exits={'W': (1, 0), 'S': (2, 1)},
        pickups=[pickup('rupee', 12, 3)],
        enemy_specs=[(80, 75, 1), (175, 155, 0)]
    )

    rooms[(2, 1)] = Room(
        'Whisper Grove', make_grove(),
        exits={'N': (2, 0), 'W': (1, 1)},
        pickups=[pickup('rupee', 8, 5)],
        enemy_specs=[(65, 125, 0), (188, 125, 0), (126, 180, 1)]
    )

    rooms[(1, -1)] = Room(
        'Hidden Shrine', make_sanctuary(),
        exits={'S': (1, 0)},
        pickups=[pickup('heart', 8, 8), pickup('rupee', 7, 8), pickup('rupee', 9, 8)],
        enemy_specs=[]
    )

    return rooms


def draw_pickups(surf, pickups):
    for p in pickups:
        if not p.get('alive', True):
            continue
        r = p['rect']
        if p['type'] == 'key':
            pygame.draw.rect(surf, C_KEY, (r.centerx - 1, r.top, 3, 7))
            pygame.draw.rect(surf, C_KEY, (r.centerx - 3, r.top, 6, 3))
            pygame.draw.rect(surf, C_KEY, (r.centerx + 1, r.bottom - 3, 4, 2))
            pygame.draw.rect(surf, (126, 94, 30), (r.centerx, r.top + 1, 1, 1))
        elif p['type'] == 'rupee':
            pygame.draw.polygon(surf, C_RUPEE, [
                (r.centerx, r.top), (r.right - 1, r.top + 3),
                (r.right - 2, r.bottom - 2), (r.centerx, r.bottom),
                (r.left + 2, r.bottom - 2), (r.left + 1, r.top + 3)
            ])
            pygame.draw.line(surf, (124, 246, 224),
                             (r.centerx - 1, r.top + 2), (r.centerx - 1, r.bottom - 2))
        elif p['type'] == 'heart':
            pygame.draw.rect(surf, C_HEART, (r.left + 1, r.top + 1, 3, 3))
            pygame.draw.rect(surf, C_HEART, (r.right - 4, r.top + 1, 3, 3))
            pygame.draw.rect(surf, C_HEART, (r.left + 1, r.top + 3, 6, 3))
            pygame.draw.rect(surf, C_HEART, (r.left + 2, r.top + 6, 4, 2))
            pygame.draw.rect(surf, C_GRASS_DARK, (r.left, r.top, 1, 1))
