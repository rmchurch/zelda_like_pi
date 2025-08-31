from __future__ import division
import pygame
from settings import UI_BG, UI_FG

def draw_hearts(surf, x, y, hp, max_hp):
    # each heart = 2 hp (half-hearts)
    hearts = (max_hp+1)//2
    full = hp//2
    half = hp%2
    for i in range(hearts):
        rx = x + i*10
        ry = y
        pygame.draw.rect(surf, (120,0,0), (rx, ry, 8, 3))
        pygame.draw.rect(surf, (180,0,0), (rx, ry+3, 8, 3))
        if i < full:
            pygame.draw.rect(surf, (255,0,0), (rx+1, ry+1, 6, 4))
        elif i == full and half:
            pygame.draw.rect(surf, (255,0,0), (rx+1, ry+1, 3, 4))
        pygame.draw.rect(surf, (0,0,0), (rx, ry, 8, 6), 1)

def draw_stats_bar(surf, player):
    # draw at top-left of the base canvas
    pygame.draw.rect(surf, UI_BG, (0,0,110,18))
    draw_hearts(surf, 4, 4, player.hp, player.max_hp)
    # rupees/keys
    font = pygame.font.Font(None, 16)
    txt = font.render("R:%d K:%d" % (player.rupees, player.keys), True, UI_FG)
    surf.blit(txt, (60, 3))
