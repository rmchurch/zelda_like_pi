from __future__ import division
import pygame
from settings import TILE, ROOM_W, ROOM_H, C_KEY, C_RUPEE
from tilemap import draw_tile, T_GRASS, T_TREE, T_WALL, T_WATER, T_SAND, T_DOOR, T_LOCK, room_solid_rects

class Room(object):
    def __init__(self, grid, exits=None, locks=None, pickups=None, enemies=None):
        self.grid = grid
        self.exits = exits or {}    # {'N': True, 'S': True, ...}
        self.locks = locks or []    # list of (i,j) lock tile locations
        self.pickups = pickups or []# list of dicts: {'type': 'key'/'rupee', 'rect': Rect, 'alive': True}
        self.enemies = enemies or []# list of enemy instances (spawned by main)

    def draw(self, surf, lock_open=False):
        for j,row in enumerate(self.grid):
            for i,tid in enumerate(row):
                draw_tile(surf, tid, i*TILE, j*TILE)

    def solid_rects(self, lock_open=False):
        return room_solid_rects(self.grid, lock_open)

def make_rect_pickup(i, j):
    return pygame.Rect(i*TILE+4, j*TILE+4, TILE-8, TILE-8)

def base_room():
    # border walls
    g = [[T_GRASS for _ in range(ROOM_W)] for __ in range(ROOM_H)]
    for i in range(ROOM_W):
        g[0][i] = T_WALL
        g[ROOM_H-1][i] = T_WALL
    for j in range(ROOM_H):
        g[j][0] = T_WALL
        g[j][ROOM_W-1] = T_WALL
    return g

def room_with_lake():
    g = base_room()
    # lake
    for j in range(5, 10):
        for i in range(4, 12):
            g[j][i] = T_WATER
    # sand shore
    for i in range(3, 13):
        g[4][i] = T_SAND
        g[10][i] = T_SAND
    for j in range(5,10):
        g[j][3] = T_SAND
        g[j][12] = T_SAND
    g[ROOM_H-1][ROOM_W//2] = T_DOOR
    g[0][ROOM_W//2] = T_DOOR
    return g

def room_with_forest():
    g = base_room()
    for j in range(3, 12, 2):
        for i in range(3, 13, 2):
            g[j][i] = T_TREE
    g[0][ROOM_W//2] = T_DOOR
    g[ROOM_H-1][ROOM_W//2] = T_DOOR
    return g

def room_with_lock():
    g = base_room()
    # locked door in north border
    g[0][ROOM_W//2] = T_LOCK
    # key in room
    key_rect = make_rect_pickup(ROOM_W//2, ROOM_H//2)
    return g, key_rect

def build_world():
    # World is a small 2x2 grid of rooms indexed by (rx, ry)
    rooms = {}

    # (0,0): start room (forest)
    rooms[(0,0)] = Room(
        grid=room_with_forest(),
        exits={'N': True, 'S': True},
        pickups=[{'type': 'rupee', 'rect': make_rect_pickup(2,2), 'alive': True}]
    )

    # (0,1): lake room (south of start)
    rooms[(0,1)] = Room(
        grid=room_with_lake(),
        exits={'N': True, 'S':True},
        pickups=[{'type':'rupee', 'rect': make_rect_pickup(12,2), 'alive': True}]
    )

    # (1,0): locked north exit, key inside
    lock_grid, key_rect = room_with_lock()
    rooms[(1,0)] = Room(
        grid=lock_grid,
        exits={'N': True},  # door is locked until you have a key
        pickups=[{'type':'key', 'rect': key_rect, 'alive': True}]
    )

    # (1,-1): a simple north room beyond the lock
    rN = base_room()
    rN[ROOM_H-1][ROOM_W//2] = T_DOOR
    rooms[(1,-1)] = Room(
        grid=rN,
        exits={'S': True},
        pickups=[{'type':'rupee', 'rect': make_rect_pickup(10,10), 'alive': True}]
    )

    return rooms

def draw_pickups(surf, pickups):
    for p in pickups:
        if not p.get('alive', True):
            continue
        if p['type'] == 'key':
            pygame.draw.rect(surf, C_KEY, p['rect'])
        elif p['type'] == 'rupee':
            pygame.draw.polygon(surf, C_RUPEE, [
                (p['rect'].centerx, p['rect'].top),
                (p['rect'].right,    p['rect'].centery-2),
                (p['rect'].centerx,  p['rect'].bottom),
                (p['rect'].left,     p['rect'].centery-2),
            ])
