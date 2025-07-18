from utils import math
from pygame.time import get_ticks
from core import *
from config import *

class Player(GameObject):
    def __init__(self):
        super().__init__(
            x = PLAYER_SPAWN_X,
            y = PLAYER_SPAWN_Y,
            width = ROCKET_RECT_WIDTH,
            height = ROCKET_RECT_HEIGHT,
            animations = ROCKET_ANIMATIONS,
            rect_color = ROCKET_RECT_COLOR
        )

        from scene import game_container as __game_container__
        self.__game_container__ = __game_container__
    
    def move(self, direction : str):
        if direction == UP:
            self.rect.y = math.clamp(self.rect.y - PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - ROCKET_RECT_HEIGHT)
        elif direction == DOWN:
            self.rect.y = math.clamp(self.rect.y + PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - ROCKET_RECT_HEIGHT)
    
    def shoot(self):
        self.__game_container__.append_child(Projectile(
            self.rect.x + ROCKET_RECT_WIDTH, 
            self.rect.y + (ROCKET_RECT_HEIGHT // 2 - 6), 
            RIGHT, 
            TAG_PROJECTILE_PLAYER
            ))
    
class Enemy(GameObject):
    def __init__(
            self,
            x : int,
            y : int,
            width : int,
            height : int,
            animations : list[Sprite],
            rect_color : tuple[int, int, int]
        ):

        super().__init__(
            x = x,
            y = y,
            width = width,
            height = height,
            tag = TAG_ENEMY,
            animations = animations,
            rect_color = rect_color
        )

        self.last_animation_time = 0
    
    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= COMET_ANIMATIONS_INTERVAL:
            self.animate()
            self.last_animation_time = get_ticks()

class Comet(Enemy):
    def __init__(
            self,
            x : int,
            y : int
        ):

        super().__init__(
            x = x,
            y = y,
            width = COMET_RECT_WIDTH,
            height = COMET_RECT_HEIGHT,
            animations = COMET_ANIMATIONS,
            rect_color = COMET_RECT_COLOR
        )

class Projectile(GameObject):
    def __init__(
        self,
        x : int,
        y : int,
        move_direction : str,
        tag : str
    ):
        super().__init__(
            x = x,
            y = y,
            width = PROJECTILE_RECT_WIDTH,
            height = PROJECTILE_RECT_HEIGHT,
            tag = tag,
            animations = PROJECTILE_ANIMATIONS,
            rect_color = PROJECTILE_RECT_COLOR
        )

        from scene import game_container as __game_container__
        self.__game_container__ = __game_container__

        self.move_direction = move_direction
    
    def update(self):
        super().update()

        self.move()

    def move(self):
        if self.move_direction == LEFT:
            self.rect.x -= PROJECTILE_SPEED
        elif self.move_direction == RIGHT:
            self.rect.x += PROJECTILE_SPEED
        
        if self.rect.x <= MAP_LEFT_BOUND or self.rect.x >= MAP_RIGHT_BOUND + PROJECTILE_RECT_WIDTH:
            self.destroy()
        
        for enemy in self.__game_container__.find_with_tag(TAG_ENEMY):
            if self.collide(enemy.rect):
                enemy.destroy()
                self.destroy()