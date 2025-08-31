from __future__ import division, print_function
import sys, argparse, pygame
from settings import BASE_W, BASE_H, SCALE, FPS
from settings import KEY_ATTACK, KEY_ITEM
from world import build_world, draw_pickups
from tilemap import room_solid_rects, T_LOCK, T_DOOR
from sprites import Player, Enemy, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
from hud import draw_stats_bar

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-audio', action='store_true', help='Disable mixer init (old Pi compatibility)')
    return ap.parse_args()

def init_pygame(no_audio=False):
    pygame.init()
    if not no_audio:
        try:
            pygame.mixer.init()
        except Exception:
            pass
    win = pygame.display.set_mode((BASE_W*SCALE, BASE_H*SCALE))
    pygame.display.set_caption("Tiny Top-Down Adventure")
    return win

def keymap():
    # pygame key state is a list; but we also want quick Z/X mapping for 2.7/1.9
    km = {
        'attack': [pygame.K_z, pygame.K_LCTRL],
        'item':   [pygame.K_x, pygame.K_LALT],
    }
    return km

def main():
    args = parse_args()
    win = init_pygame(args.no_audio)
    clock = pygame.time.Clock()

    # base canvas (logical resolution)
    canvas = pygame.Surface((BASE_W, BASE_H))

    # world
    rooms = build_world()
    rx, ry = 0, 0
    player = Player(BASE_W//2, BASE_H//2 + 50)

    # populate some enemies
    if (0,0) in rooms:
        rooms[(0,0)].enemies = [Enemy(70, 130, 0), Enemy(180, 135, 1), Enemy(30, 35, 1)]
    if (0,1) in rooms:
        rooms[(0,1)].enemies = [Enemy(120, 90,0), Enemy(30,35,1)]
    if (1,0) in rooms:
        rooms[(1,0)].enemies = [Enemy(80, 80, 1), Enemy(180, 60, 1)]

    paused = False
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_RETURN:
                    paused = not paused
                elif ev.key in (pygame.K_z, pygame.K_LCTRL):
                    player.attack()
                elif ev.key in (pygame.K_x, pygame.K_LALT):
                    player.throw_boomerang()

        if paused:
            # simple pause overlay
            canvas.fill((0,0,0))
            font = pygame.font.Font(None, 24)
            canvas.blit(font.render("PAUSED", True, (255,255,255)), (BASE_W//2-30, BASE_H//2-8))
        else:
            # update
            keys = pygame.key.get_pressed()
            room = rooms.get((rx, ry))
            lock_open = (player.keys > 0)  # simple rule: any key opens any lock
            solids = room.solid_rects(lock_open=lock_open)
            player.update(keys, solids)

            # room edge transitions (door tiles allow crossing borders)
            # Note: we keep outer walls solid; only transitions through DOOR slots at borders
            def tile_at(x, y):
                tx, ty = int(x)//16, int(y)//16
                tx = max(0, min(15, tx)); ty = max(0, min(14, ty))
                return room.grid[ty][tx]

            # north door
            if player.y < 10 and room.grid[0][8] in (T_DOOR, ):
                ry -= 1
                player.y = BASE_H - 12
            # south door
            if player.y > BASE_H-10 and room.grid[14][8] in (T_DOOR, ):
                ry += 1
                player.y = 12
            # west door
            if player.x < 10 and room.grid[7][0] in (T_DOOR, ):
                rx -= 1
                player.x = BASE_W - 12
            # east door
            if player.x > BASE_W-10 and room.grid[7][15] in (T_DOOR, ):
                rx += 1
                player.x = 12

            # locked north door (specific simple rule: position (1,0) north lock)
            if (rx, ry) == (1,0):
                # if player near top center and has a key, open and consume
                if player.y < 14:
                    if player.keys > 0:
                        player.keys -= 1
                        # convert lock tile to door tile
                        room.grid[0][8] = T_DOOR

            # pickups
            for p in room.pickups:
                if not p.get('alive', True): continue
                if player.rect().colliderect(p['rect']):
                    p['alive'] = False
                    if p['type'] == 'key':
                        player.keys += 1
                    elif p['type'] == 'rupee':
                        player.rupees += 1

            # enemies
            for e in list(room.enemies):
                e.update(player, solids)
                if e.dead:
                    room.enemies.remove(e)

            # draw
            room.draw(canvas)
            draw_pickups(canvas, room.pickups)
            for e in room.enemies:
                e.draw(canvas)
            player.draw(canvas)
            draw_stats_bar(canvas, player)

        # scale to screen
        pygame.transform.scale(canvas, win.get_size(), win)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
