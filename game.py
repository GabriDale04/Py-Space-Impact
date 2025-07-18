from utils import math
from pygame.time import get_ticks
from core import *
from config import *

class Player(GameObject):
    def __init__(self, context : Context):
        super().__init__(
            context = context,
            x = PLAYER_SPAWN_X,
            y = PLAYER_SPAWN_Y,
            width = BATTLE_SHIP_RECT_WIDTH,
            height = BATTLE_SHIP_RECT_HEIGHT,
            animations = BATTLE_SHIP_ANIMATIONS,
            rect_color = BATTLE_SHIP_RECT_COLOR
        )

        from scene import game_context as __game_context__
        self.__game_context__ = __game_context__
    
    def move(self, direction : str):
        if direction == UP:
            self.rect.y = math.clamp(self.rect.y - PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - BATTLE_SHIP_RECT_HEIGHT)
        elif direction == DOWN:
            self.rect.y = math.clamp(self.rect.y + PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - BATTLE_SHIP_RECT_HEIGHT)
    
    def shoot(self):
        self.__game_context__.append(Projectile(
            self.context,
            self.rect.x + BATTLE_SHIP_RECT_WIDTH, 
            self.rect.y + (BATTLE_SHIP_RECT_HEIGHT // 2 - 6), 
            RIGHT, 
            TAG_PROJECTILE_PLAYER
            ))
    
class Enemy(GameObject):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            width : int,
            height : int,
            animations : list[Sprite],
            rect_color : tuple[int, int, int],
            animations_interval : int,
            horizontal_speed : int,
            vertical_speed : int,
            current_direction : str,
            health : int
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            tag = TAG_ENEMY,
            animations = animations,
            rect_color = rect_color
        )

        self.last_animation_time = get_ticks()
        self.animations_interval = animations_interval

        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.current_direction = current_direction
        self.health = health
    
    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= self.animations_interval:
            self.animate()
            self.last_animation_time = get_ticks()
        
        self.move()
    
    def move(self):
        self.rect.x -= self.horizontal_speed

        if self.current_direction == UP:
            self.rect.y -= self.vertical_speed

            if self.rect.y <= MAP_TOP_BOUND:
                self.current_direction = DOWN
        elif self.current_direction == DOWN:
            self.rect.y += self.vertical_speed

            if self.rect.y + self.rect.height >= MAP_BOTTOM_BOUND:
                self.current_direction = UP

        if self.rect.x <= MAP_LEFT_BOUND - self.rect.width:
            self.destroy()

class Comet(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            current_direction : str
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = COMET_RECT_WIDTH,
            height = COMET_RECT_HEIGHT,
            animations = COMET_ANIMATIONS,
            rect_color = COMET_RECT_COLOR,
            animations_interval = COMET_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            current_direction = current_direction,
            health = COMET_HEALTH
        )

class Shuttle(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            current_direction : str
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = SHUTTLE_RECT_WIDTH,
            height = SHUTTLE_RECT_HEIGHT,
            animations = SHUTTLE_ANIMATIONS,
            rect_color = SHUTTLE_RECT_COLOR,
            animations_interval = SHUTTLE_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            current_direction = current_direction,
            health = SHUTTLE_HEALTH
        )

class Rocket(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            current_direction : str
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = ROCKET_RECT_WIDTH,
            height = ROCKET_RECT_HEIGHT,
            animations = ROCKET_ANIMATIONS,
            rect_color = ROCKET_RECT_COLOR,
            animations_interval = ROCKET_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            current_direction = current_direction,
            health = ROCKET_HEALTH
        )

class Projectile(GameObject):
    def __init__(
        self,
        context : Context,
        x : int,
        y : int,
        move_direction : str,
        tag : str
    ):
        super().__init__(
            context = context,
            x = x,
            y = y,
            width = PROJECTILE_RECT_WIDTH,
            height = PROJECTILE_RECT_HEIGHT,
            tag = tag,
            animations = PROJECTILE_ANIMATIONS,
            rect_color = PROJECTILE_RECT_COLOR
        )

        from scene import game_context as __game_context__
        self.__game_context__ = __game_context__

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
        
        for enemy in self.__game_context__.find_with_tag(TAG_ENEMY):
            if self.collide(enemy.rect):
                enemy.health -= 1

                if enemy.health == 0:
                    self.__game_context__.append(Pop(self.context, enemy.rect.x, enemy.rect.y))
                    enemy.destroy()
                
                self.destroy()

class Pop(GameObject):
    def __init__(
        self,
        context : Context,
        x : int,
        y : int      
    ):
        super().__init__(
            context = context,
            x = x,
            y = y,
            width = POP_RECT_WIDTH,
            height = POP_RECT_HEIGHT,
            animations = POP_ANIMATIONS,
            rect_color = POP_RECT_COLOR
        )

        self.spawn_time = get_ticks()
        self.last_animation_time = get_ticks()
        self.animations_interval = POP_DURATION // 2

    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= self.animations_interval:
            self.animate()
            self.last_animation_time = get_ticks()

        if get_ticks() - self.spawn_time >= POP_DURATION:
            self.destroy()