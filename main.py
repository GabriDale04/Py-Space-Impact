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
    Input.keysdown.clear()
    Input.keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            Input.keysdown.append(event.key)

    Window.screen.fill((0, 0, 0))

    game_context.update()
    game_ui_context.update()
    level1.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()