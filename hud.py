from __future__ import division
import pygame
from settings import UI_BG, UI_FG, C_HEART, C_RUPEE, C_KEY, BLACK

# The HUD changes only when hp/rupees/keys change.  Rendering fonts and heart
# polygons every frame is surprisingly expensive on Pygame 1.9 / Pi 1, so we
# keep a tiny cached 256x20 strip and simply blit it during normal gameplay.
_HUD_KEY = None
_HUD_SURFACE = None
_HUD_FONT = None


def _heart_outline(surf, x, y):
    # 8x7 pixel heart silhouette
    pts = [(x + 1, y + 1), (x + 3, y + 1), (x + 4, y + 2),
           (x + 5, y + 1), (x + 7, y + 1), (x + 8, y + 3),
           (x + 8, y + 4), (x + 4, y + 8), (x, y + 4), (x, y + 3)]
    pygame.draw.polygon(surf, (104, 28, 28), pts)
    pygame.draw.polygon(surf, BLACK, pts, 1)


def draw_hearts(surf, x, y, hp, max_hp):
    hearts = (max_hp + 1) // 2
    for i in range(hearts):
        hx = x + i * 11
        _heart_outline(surf, hx, y)
        amount = max(0, min(2, hp - i * 2))
        if amount >= 2:
            pygame.draw.rect(surf, C_HEART, (hx + 2, y + 2, 5, 3))
            pygame.draw.rect(surf, C_HEART, (hx + 3, y + 5, 3, 2))
        elif amount == 1:
            pygame.draw.rect(surf, C_HEART, (hx + 2, y + 2, 2, 4))
            pygame.draw.rect(surf, C_HEART, (hx + 3, y + 5, 1, 2))


def _build_stats_bar(player):
    global _HUD_FONT
    bar = pygame.Surface((256, 20))
    pygame.draw.rect(bar, UI_BG, (0, 0, 256, 20))
    pygame.draw.line(bar, (72, 72, 64), (0, 19), (255, 19))
    draw_hearts(bar, 4, 5, player.hp, player.max_hp)

    # rupee icon
    pygame.draw.polygon(bar, C_RUPEE, [(91, 4), (95, 7), (93, 14), (89, 14), (87, 7)])
    # key icon
    pygame.draw.rect(bar, C_KEY, (132, 5, 3, 9))
    pygame.draw.rect(bar, C_KEY, (130, 4, 7, 3))
    pygame.draw.rect(bar, C_KEY, (134, 11, 5, 2))

    if _HUD_FONT is None:
        _HUD_FONT = pygame.font.Font(None, 15)
    bar.blit(_HUD_FONT.render("x%02d" % player.rupees, True, UI_FG), (98, 5))
    bar.blit(_HUD_FONT.render("x%d" % player.keys, True, UI_FG), (142, 5))
    bar.blit(_HUD_FONT.render("Z:SWORD X:BOOM", True, (176, 176, 160)), (166, 5))
    try:
        bar = bar.convert()
    except Exception:
        pass
    return bar


def draw_stats_bar(surf, player):
    global _HUD_KEY, _HUD_SURFACE
    key = (player.hp, player.max_hp, player.rupees, player.keys)
    if key != _HUD_KEY or _HUD_SURFACE is None:
        _HUD_KEY = key
        _HUD_SURFACE = _build_stats_bar(player)
    surf.blit(_HUD_SURFACE, (0, 0))
