from core import *
from game import *
from scene import *
from levels import *

pygame.init()
Window.init()
clock = pygame.time.Clock()

level1.start()

running = True

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

    game_context.update()
    game_ui_context.update()
    level1.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()