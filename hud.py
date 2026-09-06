from __future__ import division
import pygame
from settings import UI_BG, UI_FG, C_HEART, C_RUPEE, C_KEY, BLACK


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


def draw_stats_bar(surf, player):
    # Compact, dark status strip inspired by 8-bit adventure HUDs.
    pygame.draw.rect(surf, UI_BG, (0, 0, 256, 20))
    pygame.draw.line(surf, (72, 72, 64), (0, 19), (255, 19))
    draw_hearts(surf, 4, 5, player.hp, player.max_hp)

    # rupee icon
    pygame.draw.polygon(surf, C_RUPEE, [(91, 4), (95, 7), (93, 14), (89, 14), (87, 7)])
    # key icon
    pygame.draw.rect(surf, C_KEY, (132, 5, 3, 9))
    pygame.draw.rect(surf, C_KEY, (130, 4, 7, 3))
    pygame.draw.rect(surf, C_KEY, (134, 11, 5, 2))

    font = pygame.font.Font(None, 15)
    surf.blit(font.render("x%02d" % player.rupees, True, UI_FG), (98, 5))
    surf.blit(font.render("x%d" % player.keys, True, UI_FG), (142, 5))
    surf.blit(font.render("Z:SWORD X:BOOM", True, (176, 176, 160)), (166, 5))
