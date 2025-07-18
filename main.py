from core import *
from game import *
from scene import *

pygame.init()
Window.init()
clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    Window.screen.fill((0, 0, 0))

    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]:
        player.move(UP)
    if keys[pygame.K_DOWN]:
        player.move(DOWN)

    game_container.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()