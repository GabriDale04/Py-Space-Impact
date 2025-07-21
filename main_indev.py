import config

from core import *
from game import *
from scene import *

import random

pygame.init()
Window.init()
clock = pygame.time.Clock()

running = True

last_spawn = -3000

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                player.shoot()
            elif event.key == pygame.K_r:
                player.rocket()

    Window.screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        player.move(UP)
    if keys[pygame.K_DOWN]:
        player.move(DOWN)

    if get_ticks() - last_spawn >= 3000:
        rand = random.randint(1, 3)

        Enemy_ = Comet if rand == 1 else (Shuttle if rand == 2 else Rocket)

        Enemy_(game_context, MAP_RIGHT_BOUND, random.randint(100, 500), random.randint(1, 5), random.randint(1, 3), DOWN if random.randint(0, 1) == 0 else UP)
        last_spawn = get_ticks()

    # pygame.draw.rect(Window.screen, (100, 0, 0), pygame.Rect(0, 0, WINDOW_WIDTH // 3, WINDOW_HEIGHT))
    # pygame.draw.rect(Window.screen, (0, 100, 0), pygame.Rect(WINDOW_WIDTH // 3, 0, WINDOW_WIDTH // 3, WINDOW_HEIGHT))
    # pygame.draw.rect(Window.screen, (0, 0, 100), pygame.Rect((WINDOW_WIDTH // 3) * 2, 0, WINDOW_WIDTH // 3, WINDOW_HEIGHT))

    game_context.update()
    game_ui_context.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()