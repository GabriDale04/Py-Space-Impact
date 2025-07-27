from core import *
from game import *
from scene import *
from levels import *

pygame.init()
Window.init()
clock = pygame.time.Clock()

map_bounds = pygame.Rect(MAP_LEFT_BOUND, MAP_TOP_BOUND, WINDOW_WIDTH - MAP_LEFT_BOUND - (WINDOW_WIDTH - MAP_RIGHT_BOUND), WINDOW_HEIGHT - MAP_TOP_BOUND - (WINDOW_HEIGHT - MAP_BOTTOM_BOUND))
player.shield_powerup = BattleshipShield(game_context, player)

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

    if DEBUG_SHOW_MAP_BOUNDS:
        pygame.draw.rect(Window.screen, (53, 90, 33), map_bounds)

    GameManager.update()
    game_context.update()
    game_ui_context.update()
    level_manager.update()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()