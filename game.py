from utils import math, int_b
from pygame.time import get_ticks
from core import *
from config import *
from typing import final

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

        from scene import game_context, score_text
        self.game_context = game_context
        self.score_text = score_text

        self.health = int_b(PLAYER_BASE_LIVES)
        self.score = int_b(PLAYER_BASE_SCORE)
    
    def move(self, direction : str):
        if direction == UP:
            self.rect.y = math.clamp(self.rect.y - PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - BATTLE_SHIP_RECT_HEIGHT)
        elif direction == DOWN:
            self.rect.y = math.clamp(self.rect.y + PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - BATTLE_SHIP_RECT_HEIGHT)
    
    def shoot(self):
        self.game_context.append(Projectile(
            self.context,
            self.rect.x + BATTLE_SHIP_RECT_WIDTH, 
            self.rect.y + (BATTLE_SHIP_RECT_HEIGHT // 2 - 6), 
            RIGHT, 
            TAG_PROJECTILE_PLAYER
            ))
    
    def reward(self, score : int):
        self.score += score
        self.score_text.set_amount(self.score)
    
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
        self.max_health = health
        self.health = health

        if DEBUG_SHOW_HEALTH_BARS:
            self.__health_bar_under = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)
            self.__health_bar_over = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)
    
    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= self.animations_interval:
            self.animate()
            self.last_animation_time = get_ticks()
        
        self.move()

        if DEBUG_SHOW_HEALTH_BARS:
            self.debug()
    
    @final
    def debug(self):
        self.__health_bar_under.x = self.rect.x
        self.__health_bar_under.y = self.rect.y - HEALTH_BAR_OFFSET_Y
        self.__health_bar_over.x = self.rect.x
        self.__health_bar_over.y = self.rect.y - HEALTH_BAR_OFFSET_Y
        self.__health_bar_over.width = (self.health / self.max_health) * self.__health_bar_under.width

        pygame.draw.rect(Window.screen, (128, 128, 128), self.__health_bar_under)
        pygame.draw.rect(Window.screen, (255, 0, 0), self.__health_bar_over)
    
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

        from scene import game_context, player
        self.game_context = game_context
        self.player = player

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
        
        if self.tag == TAG_PROJECTILE_PLAYER:
            for enemy in self.game_context.find_with_tag(TAG_ENEMY):
                if self.collide(enemy.rect):
                    enemy.health -= 1

                    if enemy.health == 0:
                        self.game_context.append(Pop(self.context, enemy.rect.x, enemy.rect.y))
                        enemy.destroy()
                        self.player.reward(1)

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

class LivesText(Text):
    def __init__(
            self, 
            context : Context
        ):
        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS
        )

        self.set_pos((WINDOW_WIDTH // 3 - LIVES_TEXT_ABSOLUTE_WIDTH) // 2, LIVES_TEXT_TOP_OFFSET)
        self.set_amount(PLAYER_BASE_LIVES)
    
    def set_amount(self, value : int):
        value = int_b(value)

        if value >= 0 and value <= 3:
            self.set_text("v" * value)
        else:
            self.set_text("v" + str(value).zfill(2))

class RocketsText(Text):
    def __init__(
            self, 
            context : Context
        ):

        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS
        )

        self.set_pos(WINDOW_WIDTH // 3 + (WINDOW_WIDTH // 3 - ROCKETS_TEXT_ABSOLUTE_WIDTH) // 2, ROCKETS_TEXT_TOP_OFFSET)
        self.set_amount(PLAYER_BASE_ROCKETS)
    
    def set_amount(self, value : int):
        value = int_b(value)

        self.set_text(">" + str(value).zfill(2))

class ScoreText(Text):
    def __init__(
            self, 
            context : Context
        ):

        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS
        )

        self.set_text(str(PLAYER_BASE_SCORE).zfill(5))
        self.auto_pos()

    def set_amount(self, value : int):
        text = str(int_b(value)).zfill(5)

        self.set_text(text)
        self.auto_pos()

    def auto_pos(self):
        self.set_pos(WINDOW_WIDTH // 3 * 2 + (WINDOW_WIDTH // 3 - self.width) // 2, SCORE_TEXT_TOP_OFFSET)