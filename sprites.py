from __future__ import division
import pygame
from settings import TILE, PLAYER_SPEED, ENEMY_SPEED, SLASH_TIME, INVULN_TIME, C_PLAYER, C_SWORD, C_ENEMY1, C_ENEMY2, BOOMERANG_SPEED, BOOMERANG_RANGE
from settings import C_WOOD_DARK, C_WOOD_LIGHT, C_GUARD_GOLD
from utils import Timer, clamp

DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT = 0,1,2,3

def dir_vec(d):
    return [(0,-1), (1,0), (0,1), (-1,0)][d]

class Boomerang(object):
    def __init__(self, x, y, d):
        self.x, self.y = x, y
        self.dir = d
        self.t = 0
        self.dead = False
    def rect(self):
        return pygame.Rect(int(self.x)-3, int(self.y)-3, 6, 6)
    def update(self, player_pos):
        self.t += 1
        dx, dy = dir_vec(self.dir)
        # go out then back
        if self.t * BOOMERANG_SPEED < BOOMERANG_RANGE:
            self.x += dx * BOOMERANG_SPEED
            self.y += dy * BOOMERANG_SPEED
        else:
            # home back to player
            px, py = player_pos
            vx = clamp(px - self.x, -BOOMERANG_SPEED, BOOMERANG_SPEED)
            vy = clamp(py - self.y, -BOOMERANG_SPEED, BOOMERANG_SPEED)
            self.x += vx
            self.y += vy
            if abs(px - self.x) < 6 and abs(py - self.y) < 6:
                self.dead = True
    def draw(self, surf):
        pygame.draw.rect(surf, (220,220,255), self.rect())

class Player(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 12, 12
        self.dir = DIR_DOWN
        self.hp = 6
        self.max_hp = 6
        self.keys = 0
        self.rupees = 0
        self.invuln = Timer(0)
        self.slash_timer = Timer(0)
        self.boomerangs = []

    def rect(self):
        return pygame.Rect(int(self.x)-self.w//2, int(self.y)-self.h//2, self.w, self.h)

    def center_tile(self):
        return int(self.x//TILE), int(self.y//TILE)

    def try_move(self, dx, dy, solids):
        # attempt axis-separated movement for stable collisions
        r = self.rect()
        # X
        r.x += int(dx)
        if not any(r.colliderect(s) for s in solids):
            self.x += dx
        # Y
        r = self.rect()
        r.y += int(dy)
        if not any(r.colliderect(s) for s in solids):
            self.y += dy

    def attack_rect(self):
        if not self.slash_timer.active():
            return None
        ox, oy = dir_vec(self.dir)
        r = self.rect().copy()
        # place a small slash rect in front
        if self.dir == DIR_UP:
            r.y -= 10; r.height = 8
        elif self.dir == DIR_DOWN:
            r.y += r.height; r.height = 8
        elif self.dir == DIR_LEFT:
            r.x -= 10; r.width = 8
        else:
            r.x += r.width; r.width = 8
        return r

    def update(self, keys, solids):
        self.invuln.tick()
        self.slash_timer.tick()

        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED; self.dir = DIR_LEFT
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED; self.dir = DIR_RIGHT
        if keys[pygame.K_UP]:
            dy -= PLAYER_SPEED; self.dir = DIR_UP
        if keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED; self.dir = DIR_DOWN
        #normalize diagonal (optional for old hardware skip for simplicity)

        self.try_move(dx, dy, solids)

        # boomerangs
        for b in list(self.boomerangs):
            b.update((self.x, self.y))
            if b.dead:
                self.boomerangs.remove(b)

    def take_hit(self, dmg=1, knockback=None):
        if self.invuln.active():
            return
        self.hp = max(0, self.hp - dmg)
        self.invuln.start(INVULN_TIME)
        if knockback:
            self.x += knockback[0]
            self.y += knockback[1]

    def attack(self):
        if not self.slash_timer.active():
            self.slash_timer.start(SLASH_TIME)

    def throw_boomerang(self):
        # only one at a time
        if len(self.boomerangs) == 0:
            bx, by = self.x, self.y
            self.boomerangs.append(Boomerang(bx, by, self.dir))

    def draw(self, surf):
        r = self.rect()
        # body
        col = C_PLAYER if (self.invuln.t//2)%2==0 else (180,180,180)
        pygame.draw.rect(surf, col, r)
        # face direction indicator
        if self.dir == DIR_UP:
            pygame.draw.line(surf, (0,0,0), (r.centerx-3, r.top+2), (r.centerx+3, r.top+2))
        elif self.dir == DIR_DOWN:
            pygame.draw.line(surf, (0,0,0), (r.centerx-3, r.bottom-2), (r.centerx+3, r.bottom-2))
        elif self.dir == DIR_LEFT:
            pygame.draw.line(surf, (0,0,0), (r.left+2, r.centery-3), (r.left+2, r.centery+3))
        else:
            pygame.draw.line(surf, (0,0,0), (r.right-2, r.centery-3), (r.right-2, r.centery+3))

        # sword slash
        #ar = self.attack_rect()
        #if ar:
        #    pygame.draw.rect(surf, C_SWORD, ar)
        if self.slash_timer.active():
            self.draw_wooden_sword(surf)

        # boomerang
        for b in self.boomerangs:
            b.draw(surf)

    def draw_wooden_sword(self, surf):
        # Only visible while slashing; collision still uses attack_rect()
        if not self.slash_timer.active():
            return

        r = self.rect()
        cx, cy = r.centerx, r.centery

        # pixel sizes (tweak to taste)
        blade_w, blade_h = 4, 12   # thickness x length
        guard_w, guard_h = 8, 2
        grip_w,  grip_h  = 4, 4

        if self.dir == 0:  # DIR_UP
            blade = pygame.Rect(cx - blade_w//2, r.top - blade_h - 2, blade_w, blade_h)
            guard = pygame.Rect(cx - guard_w//2, r.top - 2,            guard_w, guard_h)
            grip  = pygame.Rect(cx - grip_w//2,  r.top + 2,            grip_w,  grip_h)
        elif self.dir == 2:  # DIR_DOWN
            guard = pygame.Rect(cx - guard_w//2, r.bottom,             guard_w, guard_h)
            blade = pygame.Rect(cx - blade_w//2, r.bottom + guard_h,   blade_w, blade_h)
            grip  = pygame.Rect(cx - grip_w//2,  r.bottom - grip_h,    grip_w,  grip_h)
        elif self.dir == 3:  # DIR_LEFT
            blade = pygame.Rect(r.left - blade_h - 2, cy - blade_w//2, blade_h, blade_w)
            guard = pygame.Rect(r.left - 2,           cy - guard_w//2, 2,       guard_w)
            grip  = pygame.Rect(r.left + 0,           cy - grip_w//2,  grip_h,  grip_w)  # small square by body
        else:  # DIR_RIGHT (1)
            guard = pygame.Rect(r.right,              cy - guard_w//2, 2,       guard_w)
            blade = pygame.Rect(r.right + 2,          cy - blade_w//2, blade_h, blade_w)
            grip  = pygame.Rect(r.right - grip_h,     cy - grip_w//2,  grip_h,  grip_w)

        # draw: blade, guard, grip
        pygame.draw.rect(surf, C_WOOD_LIGHT, blade)
        pygame.draw.rect(surf, C_GUARD_GOLD, guard)
        pygame.draw.rect(surf, C_WOOD_DARK,  grip)

class Enemy(object):
    def __init__(self, x, y, kind=0):
        self.x, self.y = x, y
        self.kind = kind
        self.w, self.h = 12, 12
        self.hp = 2 if kind==0 else 3
        self.t = 0
        self.dead = False

    def rect(self):
        return pygame.Rect(int(self.x)-self.w//2, int(self.y)-self.h//2, self.w, self.h)

    def update(self, player, solids):
        self.t += 1
        # simple wander & chase
        if self.t % 60 < 30:
            # drift toward player a bit
            dx = ENEMY_SPEED if player.x > self.x else -ENEMY_SPEED
            dy = ENEMY_SPEED if player.y > self.y else -ENEMY_SPEED
        else:
            # random-ish wiggle
            dx = ( (self.t%7)-3 ) * 0.1
            dy = ( (self.t%5)-2 ) * 0.1

        r = self.rect()
        r.x += int(dx)
        if not any(r.colliderect(s) for s in solids):
            self.x += dx
        r = self.rect()
        r.y += int(dy)
        if not any(r.colliderect(s) for s in solids):
            self.y += dy

        # contact damage
        if self.rect().colliderect(player.rect()):
            player.take_hit(1, ( (player.x-self.x)*0.2, (player.y-self.y)*0.2 ))

        # hit by sword
        ar = player.attack_rect()
        if ar and ar.colliderect(self.rect()):
            self.hp -= 1
            if self.hp <= 0:
                self.dead = True

        # hit by boomerang (stuns/kills weak)
        for b in list(player.boomerangs):
            if b.rect().colliderect(self.rect()):
                self.hp -= self.hp
                player.boomerangs.remove(b)
                if self.hp <= 0:
                    self.dead = True

    def draw(self, surf):
        r = self.rect()
        col = C_ENEMY1 if self.kind==0 else C_ENEMY2
        pygame.draw.rect(surf, col, r)
        # eyes
        pygame.draw.rect(surf, (0,0,0), (r.x+3, r.y+3, 2, 2))
        pygame.draw.rect(surf, (0,0,0), (r.right-5, r.y+3, 2, 2))
