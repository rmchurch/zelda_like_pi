from __future__ import division, print_function
import argparse
import pygame
from settings import BASE_W, BASE_H, SCALE, FPS, ROOM_BANNER_TIME
from world import build_world, draw_pickups
from tilemap import T_DOOR
from sprites import Player, Enemy
from hud import draw_stats_bar


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-audio', action='store_true',
                    help='Disable mixer init (old Pi compatibility)')
    ap.add_argument('--scale', type=int, default=SCALE,
                    help='Integer window scale (default from settings.py)')
    return ap.parse_args()


def init_pygame(no_audio=False, scale=SCALE):
    pygame.init()
    if not no_audio:
        try:
            pygame.mixer.init()
        except Exception:
            pass
    scale = max(1, int(scale))
    win = pygame.display.set_mode((BASE_W * scale, BASE_H * scale))
    pygame.display.set_caption('Tiny Top-Down Adventure - Modern Refresh')
    return win


def reset_game():
    rooms = build_world()
    player = Player(BASE_W // 2, BASE_H // 2 + 35)
    return rooms, player, (0, 0)


def ensure_room_spawned(room):
    if room.spawned:
        return
    room.enemies = [Enemy(x, y, kind) for (x, y, kind) in room.enemy_specs]
    room.spawned = True


def add_drop(room, enemy):
    if not enemy.drop_type:
        return
    room.pickups.append({
        'type': enemy.drop_type,
        'rect': pygame.Rect(int(enemy.x) - 4, int(enemy.y) - 4, 8, 8),
        'alive': True,
    })


def process_pickups(room, player):
    for p in room.pickups:
        if not p.get('alive', True):
            continue
        if not player.rect().colliderect(p['rect']):
            continue
        kind = p['type']
        if kind == 'heart' and player.hp >= player.max_hp:
            continue
        p['alive'] = False
        if kind == 'key':
            player.keys += 1
        elif kind == 'rupee':
            player.rupees += 1
        elif kind == 'heart':
            player.heal(2)


def maybe_room_clear_reward(room):
    if room.cleared_reward or not room.enemy_specs or room.enemies:
        return
    room.cleared_reward = True
    # One small reward per cleared combat room.
    room.pickups.append({
        'type': 'rupee',
        'rect': pygame.Rect(BASE_W // 2 - 4, BASE_H // 2 - 4, 8, 8),
        'alive': True,
    })


def transition_if_needed(rooms, room_pos, room, player):
    side = None
    if player.y < 4:
        side = 'N'
    elif player.y > BASE_H - 4:
        side = 'S'
    elif player.x < 4:
        side = 'W'
    elif player.x > BASE_W - 4:
        side = 'E'

    if side is None:
        return room_pos, False

    target = room.exits.get(side)
    if target is None or target not in rooms or room.tile_for_side(side) != T_DOOR:
        # Defensive clamp: never allow a transition into a missing room.
        player.x = max(8, min(BASE_W - 8, player.x))
        player.y = max(8, min(BASE_H - 8, player.y))
        return room_pos, False

    if side == 'N':
        player.y = BASE_H - 10
    elif side == 'S':
        player.y = 10
    elif side == 'W':
        player.x = BASE_W - 10
    elif side == 'E':
        player.x = 10
    return target, True


def draw_room_name(surf, font, room, frames_left):
    if frames_left <= 0:
        return
    text = font.render(room.name, True, (244, 232, 184))
    pad = 5
    box = pygame.Rect(BASE_W // 2 - text.get_width() // 2 - pad,
                      23, text.get_width() + pad * 2, 15)
    pygame.draw.rect(surf, (12, 12, 12), box)
    pygame.draw.rect(surf, (104, 88, 54), box, 1)
    surf.blit(text, (box.x + pad, box.y + 2))


def draw_pause(surf, title_font, font):
    panel = pygame.Rect(46, 65, 164, 104)
    pygame.draw.rect(surf, (10, 10, 12), panel)
    pygame.draw.rect(surf, (202, 182, 108), panel, 2)
    title = title_font.render('PAUSED', True, (244, 232, 184))
    surf.blit(title, (BASE_W // 2 - title.get_width() // 2, 76))
    lines = [
        'ARROWS   move',
        'Z / CTRL sword',
        'X / ALT  boomerang',
        'ENTER    resume',
        'ESC      quit',
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, (210, 210, 194))
        surf.blit(txt, (68, 103 + i * 11))


def draw_game_over(surf, title_font, font):
    panel = pygame.Rect(48, 82, 160, 70)
    pygame.draw.rect(surf, (8, 8, 8), panel)
    pygame.draw.rect(surf, (172, 56, 48), panel, 2)
    title = title_font.render('GAME OVER', True, (238, 84, 68))
    surf.blit(title, (BASE_W // 2 - title.get_width() // 2, 94))
    msg = font.render('Press R to begin again', True, (236, 224, 196))
    surf.blit(msg, (BASE_W // 2 - msg.get_width() // 2, 126))


def draw_scene(canvas, room, player, phase, banner_font, banner_frames):
    room.draw(canvas, phase)
    draw_pickups(canvas, room.pickups)
    for enemy in room.enemies:
        enemy.draw(canvas)
    player.draw(canvas)
    draw_stats_bar(canvas, player)
    draw_room_name(canvas, banner_font, room, banner_frames)


def main():
    args = parse_args()
    win = init_pygame(args.no_audio, args.scale)
    clock = pygame.time.Clock()
    # At scale 1, draw straight to the display and skip the full-screen
    # software scaling pass entirely.  Otherwise keep one converted logical
    # canvas for fast blits.
    if win.get_size() == (BASE_W, BASE_H):
        canvas = win
    else:
        canvas = pygame.Surface((BASE_W, BASE_H)).convert()
    font = pygame.font.Font(None, 16)
    title_font = pygame.font.Font(None, 24)
    banner_font = pygame.font.Font(None, 15)

    rooms, player, room_pos = reset_game()
    ensure_room_spawned(rooms[room_pos])
    banner_frames = ROOM_BANNER_TIME
    paused = False
    running = True

    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif player.hp <= 0 and ev.key == pygame.K_r:
                    rooms, player, room_pos = reset_game()
                    ensure_room_spawned(rooms[room_pos])
                    banner_frames = ROOM_BANNER_TIME
                    paused = False
                elif ev.key == pygame.K_RETURN and player.hp > 0:
                    paused = not paused
                elif not paused and player.hp > 0:
                    if ev.key in (pygame.K_z, pygame.K_LCTRL):
                        player.attack()
                    elif ev.key in (pygame.K_x, pygame.K_LALT):
                        player.throw_boomerang()

        room = rooms[room_pos]
        phase = (pygame.time.get_ticks() // 350) % 2

        if not paused and player.hp > 0:
            ensure_room_spawned(room)
            solids = room.solid_rects()
            keys = pygame.key.get_pressed()
            player.update(keys, solids)

            # A key opens only the actual locked doorway the hero is touching.
            # Rebuild collision data only on the rare frame when a door changes.
            if room.unlock_near_player(player):
                solids = room.solid_rects()

            new_pos, changed = transition_if_needed(rooms, room_pos, room, player)
            if changed:
                room_pos = new_pos
                room = rooms[room_pos]
                ensure_room_spawned(room)
                banner_frames = ROOM_BANNER_TIME
                # Do not run old-room combat/pickups on the transition frame.
            else:
                process_pickups(room, player)
                # Reuse the same cached collision rectangles for every enemy.
                # Iterate backwards so dead enemies can be removed without
                # allocating a copy of the list every frame.
                i = len(room.enemies) - 1
                while i >= 0:
                    enemy = room.enemies[i]
                    enemy.update(player, solids)
                    if enemy.dead:
                        add_drop(room, enemy)
                        room.enemies.pop(i)
                    i -= 1
                maybe_room_clear_reward(room)

            if banner_frames > 0:
                banner_frames -= 1

        draw_scene(canvas, room, player, phase, banner_font, banner_frames)
        if paused:
            draw_pause(canvas, title_font, font)
        elif player.hp <= 0:
            draw_game_over(canvas, title_font, font)

        if canvas is not win:
            pygame.transform.scale(canvas, win.get_size(), win)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
