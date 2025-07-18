from pygame.time import get_ticks
from core import *
from config import *

class Player(GameObject):
    def __init__(self):
        super().__init__(
            x = 0,
            y = 0,
            width = ROCKET_RECT_WIDTH,
            height = ROCKET_RECT_HEIGHT,
            animations = ROCKET_ANIMATIONS,
            rect_color = ROCKET_RECT_COLOR
        )
    
    def move(self, direction : str):
        if direction == UP:
            self.rect.y -= PLAYER_SPEED
        elif direction == DOWN:
            self.rect.y += PLAYER_SPEED

class StarShip(GameObject):
    def __init__(
            self,
            x : int,
            y : int
        ):

        super().__init__(
            x = x,
            y = y,
            width = STAR_SHIP_RECT_WIDTH,
            height = STAR_SHIP_RECT_HEIGHT,
            animations = STAR_SHIP_ANIMATIONS
        )

        self.last_animation_time = 0
    
    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= STAR_SHIP_ANIMATIONS_INTERVAL:
            self.animate()
            self.last_animation_time = get_ticks()