from __future__ import division
import math
import pygame
from settings import (
    TILE, PLAYER_SPEED, ENEMY_SPEED, SLASH_TIME, ATTACK_COOLDOWN,
    INVULN_TIME, ENEMY_HURT_TIME, ENEMY_STUN_TIME,
    BOOMERANG_SPEED, BOOMERANG_RANGE,
    C_TUNIC, C_TUNIC_DARK, C_SKIN, C_HAIR, C_BOOT, C_BELT,
    C_SHIELD, C_SHIELD_TRIM,
    C_ENEMY1, C_ENEMY2, C_ENEMY_DARK,
    C_WOOD_DARK, C_WOOD_LIGHT, C_GUARD_GOLD, WHITE, BLACK
)
from utils import Timer, clamp

DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT = 0, 1, 2, 3

# Procedural art is rendered into tiny colorkey surfaces once, then blitted.
# This preserves the asset-free design while avoiding dozens of pygame.draw
# calls per actor on every frame.
_TRANSPARENT = (255, 0, 255)
_PLAYER_FRAME_CACHE = {}
_ENEMY_FRAME_CACHE = {}


def dir_vec(d):
    return [(0, -1), (1, 0), (0, 1), (-1, 0)][d]


def _rect(surf, color, x, y, w, h):
    pygame.draw.rect(surf, color, (int(x), int(y), int(w), int(h)))


def _overlaps_solid(test, solids):
    # Explicit loop is noticeably cheaper than creating a generator for every
    # movement axis on Python 2.7.
    for solid in solids:
        if test.colliderect(solid):
            return True
    return False


def _move_rect_axis(owner, dx, dy, solids):
    if dx:
        test = owner.rect()
        test.x += int(round(dx))
        if not _overlaps_solid(test, solids):
            owner.x += dx
    if dy:
        test = owner.rect()
        test.y += int(round(dy))
        if not _overlaps_solid(test, solids):
            owner.y += dy


class Boomerang(object):
    def __init__(self, x, y, d):
        self.x, self.y = x, y
        self.dir = d
        self.distance = 0.0
        self.returning = False
        self.dead = False
        self.spin = 0
        self.hit_ids = set()

    def rect(self):
        return pygame.Rect(int(self.x) - 4, int(self.y) - 4, 8, 8)

    def update(self, player_pos):
        self.spin = (self.spin + 2) % 12
        if not self.returning:
            dx, dy = dir_vec(self.dir)
            self.x += dx * BOOMERANG_SPEED
            self.y += dy * BOOMERANG_SPEED
            self.distance += BOOMERANG_SPEED
            if self.distance >= BOOMERANG_RANGE:
                self.returning = True
        else:
            px, py = player_pos
            vx = px - self.x
            vy = py - self.y
            dist = math.sqrt(vx * vx + vy * vy)
            if dist <= BOOMERANG_SPEED + 4:
                self.dead = True
                return
            if dist > 0:
                self.x += (vx / dist) * BOOMERANG_SPEED
                self.y += (vy / dist) * BOOMERANG_SPEED

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if (self.spin // 3) % 2 == 0:
            _rect(surf, C_WOOD_LIGHT, x - 4, y - 3, 7, 2)
            _rect(surf, C_WOOD_LIGHT, x + 1, y - 3, 2, 6)
            _rect(surf, C_WOOD_DARK, x - 4, y - 2, 2, 2)
        else:
            _rect(surf, C_WOOD_LIGHT, x - 3, y - 4, 2, 7)
            _rect(surf, C_WOOD_LIGHT, x - 3, y + 1, 6, 2)
            _rect(surf, C_WOOD_DARK, x - 2, y - 4, 2, 2)


class Player(object):
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 10, 11
        self.dir = DIR_DOWN
        self.hp = 6
        self.max_hp = 6
        self.keys = 0
        self.rupees = 0
        self.invuln = Timer(0)
        self.slash_timer = Timer(0)
        self.attack_cooldown = Timer(0)
        self.boomerangs = []
        self.attack_id = 0
        self.walk_clock = 0
        self.moving = False

    def rect(self):
        # Collision box hugs the torso/feet, not the whole 16x16 sprite/cap.
        return pygame.Rect(int(self.x) - self.w // 2,
                           int(self.y) - self.h // 2 + 1,
                           self.w, self.h)

    def center_tile(self):
        return int(self.x // TILE), int(self.y // TILE)

    def try_move(self, dx, dy, solids):
        _move_rect_axis(self, dx, dy, solids)

    def attack_rect(self):
        if not self.slash_timer.active():
            return None
        body = self.rect()
        if self.dir == DIR_UP:
            return pygame.Rect(body.centerx - 4, body.top - 13, 8, 14)
        if self.dir == DIR_DOWN:
            return pygame.Rect(body.centerx - 4, body.bottom - 1, 8, 14)
        if self.dir == DIR_LEFT:
            return pygame.Rect(body.left - 13, body.centery - 4, 14, 8)
        return pygame.Rect(body.right - 1, body.centery - 4, 14, 8)

    def update(self, keys, solids):
        self.invuln.tick()
        self.slash_timer.tick()
        self.attack_cooldown.tick()

        dx = dy = 0.0
        if keys[pygame.K_LEFT]:
            dx -= 1.0
        if keys[pygame.K_RIGHT]:
            dx += 1.0
        if keys[pygame.K_UP]:
            dy -= 1.0
        if keys[pygame.K_DOWN]:
            dy += 1.0

        self.moving = (dx != 0.0 or dy != 0.0)
        if self.moving:
            # Prefer the stronger axis when choosing facing during diagonal movement.
            if abs(dx) >= abs(dy) and dx != 0:
                self.dir = DIR_RIGHT if dx > 0 else DIR_LEFT
            elif dy != 0:
                self.dir = DIR_DOWN if dy > 0 else DIR_UP

            if dx and dy:
                dx *= 0.70710678
                dy *= 0.70710678

            speed = PLAYER_SPEED * (0.72 if self.slash_timer.active() else 1.0)
            self.try_move(dx * speed, dy * speed, solids)
            self.walk_clock += 1
        else:
            self.walk_clock = 0

        for b in list(self.boomerangs):
            b.update((self.x, self.y))
            if b.dead:
                self.boomerangs.remove(b)

    def take_hit(self, dmg=1, knockback=None):
        if self.invuln.active() or self.hp <= 0:
            return False
        self.hp = max(0, self.hp - dmg)
        self.invuln.start(INVULN_TIME)
        if knockback:
            self.x += clamp(knockback[0], -5, 5)
            self.y += clamp(knockback[1], -5, 5)
        return True

    def heal(self, amount=2):
        self.hp = min(self.max_hp, self.hp + amount)

    def attack(self):
        if self.attack_cooldown.active() or self.hp <= 0:
            return False
        self.attack_id += 1
        self.slash_timer.start(SLASH_TIME)
        self.attack_cooldown.start(SLASH_TIME + ATTACK_COOLDOWN)
        return True

    def throw_boomerang(self):
        if self.hp <= 0 or self.slash_timer.active():
            return False
        if len(self.boomerangs) == 0:
            self.boomerangs.append(Boomerang(self.x, self.y, self.dir))
            return True
        return False

    def _draw_shadow(self, surf, sx, sy):
        _rect(surf, (28, 74, 38), sx + 4, sy + 14, 9, 2)

    def _draw_front(self, surf, sx, sy, step):
        # Long green cap and brown hair
        _rect(surf, C_TUNIC_DARK, sx + 4, sy, 7, 2)
        _rect(surf, C_TUNIC, sx + 3, sy + 2, 9, 3)
        _rect(surf, C_TUNIC, sx + 1, sy + 3, 4, 2)
        _rect(surf, C_HAIR, sx + 4, sy + 5, 8, 2)
        # face
        _rect(surf, C_SKIN, sx + 5, sy + 6, 7, 4)
        _rect(surf, BLACK, sx + 6, sy + 7, 1, 1)
        _rect(surf, BLACK, sx + 10, sy + 7, 1, 1)
        # ears/hands
        _rect(surf, C_SKIN, sx + 3, sy + 7, 2, 2)
        _rect(surf, C_SKIN, sx + 12, sy + 7, 2, 2)
        # tunic and belt
        _rect(surf, C_TUNIC_DARK, sx + 4, sy + 10, 9, 4)
        _rect(surf, C_TUNIC, sx + 5, sy + 10, 7, 3)
        _rect(surf, C_BELT, sx + 5, sy + 13, 7, 1)
        # legs alternate one pixel for walking
        _rect(surf, C_SKIN, sx + 5, sy + 14, 2, 1 + step)
        _rect(surf, C_SKIN, sx + 10, sy + 14 + step, 2, 1)
        _rect(surf, C_BOOT, sx + 4, sy + 15, 3, 1)
        _rect(surf, C_BOOT, sx + 10, sy + 15, 3, 1)

    def _draw_back(self, surf, sx, sy, step):
        _rect(surf, C_TUNIC_DARK, sx + 4, sy, 7, 2)
        _rect(surf, C_TUNIC, sx + 3, sy + 2, 9, 4)
        _rect(surf, C_TUNIC, sx + 1, sy + 2, 4, 2)
        _rect(surf, C_HAIR, sx + 4, sy + 5, 8, 3)
        _rect(surf, C_TUNIC_DARK, sx + 4, sy + 8, 9, 6)
        # shield on back
        _rect(surf, C_SHIELD_TRIM, sx + 6, sy + 8, 6, 6)
        _rect(surf, C_SHIELD, sx + 7, sy + 9, 4, 5)
        _rect(surf, C_SHIELD_TRIM, sx + 8, sy + 10, 2, 1)
        _rect(surf, C_BELT, sx + 4, sy + 13, 9, 1)
        _rect(surf, C_BOOT, sx + 4 + step, sy + 15, 3, 1)
        _rect(surf, C_BOOT, sx + 10 - step, sy + 15, 3, 1)

    def _draw_side(self, surf, sx, sy, facing_right, step):
        # cap points behind the hero
        if facing_right:
            _rect(surf, C_TUNIC_DARK, sx + 4, sy, 7, 2)
            _rect(surf, C_TUNIC, sx + 3, sy + 2, 9, 3)
            _rect(surf, C_TUNIC, sx + 1, sy + 3, 4, 2)
            _rect(surf, C_HAIR, sx + 5, sy + 5, 6, 3)
            _rect(surf, C_SKIN, sx + 8, sy + 6, 5, 4)
            _rect(surf, BLACK, sx + 11, sy + 7, 1, 1)
            _rect(surf, C_SKIN, sx + 13, sy + 8, 2, 1)
            _rect(surf, C_TUNIC_DARK, sx + 5, sy + 10, 8, 4)
            _rect(surf, C_SHIELD_TRIM, sx + 4, sy + 9, 3, 5)
            _rect(surf, C_SHIELD, sx + 4, sy + 10, 2, 3)
        else:
            _rect(surf, C_TUNIC_DARK, sx + 5, sy, 7, 2)
            _rect(surf, C_TUNIC, sx + 4, sy + 2, 9, 3)
            _rect(surf, C_TUNIC, sx + 11, sy + 3, 4, 2)
            _rect(surf, C_HAIR, sx + 5, sy + 5, 6, 3)
            _rect(surf, C_SKIN, sx + 3, sy + 6, 5, 4)
            _rect(surf, BLACK, sx + 4, sy + 7, 1, 1)
            _rect(surf, C_SKIN, sx + 1, sy + 8, 2, 1)
            _rect(surf, C_TUNIC_DARK, sx + 4, sy + 10, 8, 4)
            _rect(surf, C_SHIELD_TRIM, sx + 11, sy + 9, 3, 5)
            _rect(surf, C_SHIELD, sx + 12, sy + 10, 2, 3)
        _rect(surf, C_BELT, sx + 5, sy + 13, 7, 1)
        _rect(surf, C_BOOT, sx + 5 + step, sy + 15, 3, 1)
        _rect(surf, C_BOOT, sx + 10 - step, sy + 15, 3, 1)

    def draw(self, surf):
        sx, sy = int(self.x) - 8, int(self.y) - 9
        step = 1 if self.moving and ((self.walk_clock // 3) % 2) else 0
        self._draw_shadow(surf, sx, sy)

        # Zelda-like flicker: skip the body on alternating invulnerability frames.
        body_visible = not self.invuln.active() or ((self.invuln.t // 3) % 2 == 0)
        if body_visible:
            key = (self.dir, step)
            frame = _PLAYER_FRAME_CACHE.get(key)
            if frame is None:
                frame = pygame.Surface((16, 16))
                frame.fill(_TRANSPARENT)
                frame.set_colorkey(_TRANSPARENT)
                if self.dir == DIR_DOWN:
                    self._draw_front(frame, 0, 0, step)
                elif self.dir == DIR_UP:
                    self._draw_back(frame, 0, 0, step)
                elif self.dir == DIR_RIGHT:
                    self._draw_side(frame, 0, 0, True, step)
                else:
                    self._draw_side(frame, 0, 0, False, step)
                try:
                    frame = frame.convert()
                    frame.set_colorkey(_TRANSPARENT)
                except Exception:
                    pass
                _PLAYER_FRAME_CACHE[key] = frame
            surf.blit(frame, (sx, sy))

        if self.slash_timer.active():
            self.draw_sword(surf)
        for b in self.boomerangs:
            b.draw(surf)

    def draw_sword(self, surf):
        body = self.rect()
        cx, cy = body.centerx, body.centery
        blade = C_WOOD_LIGHT
        shine = (222, 158, 80)
        if self.dir == DIR_UP:
            _rect(surf, C_WOOD_DARK, cx - 1, body.top - 1, 2, 4)
            _rect(surf, C_GUARD_GOLD, cx - 4, body.top - 3, 8, 2)
            _rect(surf, blade, cx - 2, body.top - 13, 4, 10)
            _rect(surf, shine, cx - 1, body.top - 12, 1, 8)
            _rect(surf, blade, cx - 1, body.top - 15, 2, 2)
        elif self.dir == DIR_DOWN:
            _rect(surf, C_WOOD_DARK, cx - 1, body.bottom - 3, 2, 4)
            _rect(surf, C_GUARD_GOLD, cx - 4, body.bottom + 1, 8, 2)
            _rect(surf, blade, cx - 2, body.bottom + 3, 4, 10)
            _rect(surf, shine, cx - 1, body.bottom + 4, 1, 8)
            _rect(surf, blade, cx - 1, body.bottom + 13, 2, 2)
        elif self.dir == DIR_LEFT:
            _rect(surf, C_WOOD_DARK, body.left - 2, cy - 1, 4, 2)
            _rect(surf, C_GUARD_GOLD, body.left - 4, cy - 4, 2, 8)
            _rect(surf, blade, body.left - 14, cy - 2, 10, 4)
            _rect(surf, shine, body.left - 13, cy - 1, 8, 1)
            _rect(surf, blade, body.left - 16, cy - 1, 2, 2)
        else:
            _rect(surf, C_WOOD_DARK, body.right - 2, cy - 1, 4, 2)
            _rect(surf, C_GUARD_GOLD, body.right + 2, cy - 4, 2, 8)
            _rect(surf, blade, body.right + 4, cy - 2, 10, 4)
            _rect(surf, shine, body.right + 5, cy - 1, 8, 1)
            _rect(surf, blade, body.right + 14, cy - 1, 2, 2)


def _get_enemy_frame(kind, flash):
    key = (kind, bool(flash))
    frame = _ENEMY_FRAME_CACHE.get(key)
    if frame is not None:
        return frame

    frame = pygame.Surface((16, 16))
    frame.fill(_TRANSPARENT)
    frame.set_colorkey(_TRANSPARENT)
    x = y = 0
    main = WHITE if flash else (C_ENEMY1 if kind == 0 else C_ENEMY2)

    # shadow
    _rect(frame, (34, 68, 32), x + 3, y + 13, 11, 2)

    if kind == 0:
        _rect(frame, C_ENEMY_DARK, x + 4, y + 3, 8, 10)
        _rect(frame, main, x + 3, y + 4, 10, 8)
        _rect(frame, main, x + 5, y + 2, 6, 3)
        _rect(frame, C_ENEMY_DARK, x + 1, y + 6, 3, 4)
        _rect(frame, C_ENEMY_DARK, x + 12, y + 6, 3, 4)
        _rect(frame, BLACK, x + 5, y + 5, 2, 2)
        _rect(frame, BLACK, x + 10, y + 5, 2, 2)
        _rect(frame, WHITE if flash else (236, 116, 74), x + 6, y + 8, 5, 3)
        _rect(frame, C_ENEMY_DARK, x + 3, y + 12, 3, 2)
        _rect(frame, C_ENEMY_DARK, x + 10, y + 12, 3, 2)
    else:
        _rect(frame, C_ENEMY_DARK, x + 4, y + 2, 9, 12)
        _rect(frame, main, x + 3, y + 3, 10, 9)
        pygame.draw.polygon(frame, main, [(x + 3, y + 5), (x, y + 3), (x + 3, y + 8)])
        pygame.draw.polygon(frame, main, [(x + 13, y + 5), (x + 15, y + 3), (x + 13, y + 8)])
        _rect(frame, C_ENEMY_DARK, x + 4, y + 3, 8, 2)
        _rect(frame, BLACK, x + 5, y + 6, 2, 2)
        _rect(frame, BLACK, x + 10, y + 6, 2, 2)
        _rect(frame, C_ENEMY_DARK, x + 7, y + 9, 3, 1)
        _rect(frame, C_SHIELD_TRIM, x + 9, y + 10, 5, 5)
        _rect(frame, C_SHIELD, x + 10, y + 11, 3, 4)
        _rect(frame, C_BOOT, x + 4, y + 13, 3, 2)
        _rect(frame, C_BOOT, x + 10, y + 13, 3, 2)

    try:
        frame = frame.convert()
        frame.set_colorkey(_TRANSPARENT)
    except Exception:
        pass
    _ENEMY_FRAME_CACHE[key] = frame
    return frame


class Enemy(object):
    def __init__(self, x, y, kind=0):
        self.x, self.y = float(x), float(y)
        self.kind = kind
        self.w, self.h = (12, 10) if kind == 0 else (12, 12)
        self.hp = 2 if kind == 0 else 3
        self.t = 0
        self.dead = False
        self.facing = DIR_DOWN
        self.hurt_timer = Timer(0)
        self.stun_timer = Timer(0)
        self.last_attack_id = -1
        self.drop_type = None

    def rect(self):
        return pygame.Rect(int(self.x) - self.w // 2,
                           int(self.y) - self.h // 2,
                           self.w, self.h)

    def _choose_motion(self, player):
        vx = player.x - self.x
        vy = player.y - self.y
        dist2 = vx * vx + vy * vy

        if dist2 < 95 * 95:
            if abs(vx) > abs(vy):
                self.facing = DIR_RIGHT if vx > 0 else DIR_LEFT
            else:
                self.facing = DIR_DOWN if vy > 0 else DIR_UP
            dist = math.sqrt(dist2) if dist2 > 0 else 1.0
            return (vx / dist) * ENEMY_SPEED, (vy / dist) * ENEMY_SPEED

        # deterministic four-direction wandering keeps old-Pi CPU cost tiny.
        cycle = (self.t // 35 + self.kind * 2) % 4
        self.facing = [DIR_RIGHT, DIR_DOWN, DIR_LEFT, DIR_UP][cycle]
        dx, dy = dir_vec(self.facing)
        return dx * ENEMY_SPEED * 0.72, dy * ENEMY_SPEED * 0.72

    def _hurt(self, damage, player):
        self.hp -= damage
        self.hurt_timer.start(ENEMY_HURT_TIME)
        self.stun_timer.start(6)
        dx = self.x - player.x
        dy = self.y - player.y
        mag = math.sqrt(dx * dx + dy * dy) or 1.0
        self.x += (dx / mag) * 4.0
        self.y += (dy / mag) * 4.0
        if self.hp <= 0:
            self.dead = True
            code = (int(self.x) + int(self.y) + self.kind * 3) % 5
            self.drop_type = 'heart' if code == 0 else ('rupee' if code in (1, 2, 3) else None)

    def update(self, player, solids):
        self.t += 1
        self.hurt_timer.tick()
        self.stun_timer.tick()

        if not self.stun_timer.active() and not self.dead:
            dx, dy = self._choose_motion(player)
            _move_rect_axis(self, dx, dy, solids)

        if self.rect().colliderect(player.rect()):
            dx = player.x - self.x
            dy = player.y - self.y
            mag = math.sqrt(dx * dx + dy * dy) or 1.0
            player.take_hit(1, ((dx / mag) * 4, (dy / mag) * 4))

        ar = player.attack_rect()
        if (ar and ar.colliderect(self.rect()) and
                self.last_attack_id != player.attack_id and not self.dead):
            self.last_attack_id = player.attack_id
            self._hurt(1, player)

        # Boomerang stuns rather than deleting enemies outright.
        for b in list(player.boomerangs):
            marker = id(self)
            if marker not in b.hit_ids and b.rect().colliderect(self.rect()):
                b.hit_ids.add(marker)
                b.returning = True
                self.stun_timer.start(ENEMY_STUN_TIME)

    def draw(self, surf):
        r = self.rect()
        flash = self.hurt_timer.active() and ((self.hurt_timer.t // 2) % 2 == 0)
        frame = _get_enemy_frame(self.kind, flash)
        surf.blit(frame, (r.centerx - 8, r.centery - 8))
