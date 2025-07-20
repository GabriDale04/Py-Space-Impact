from utils import clamp, int_b
from pygame.time import get_ticks
from core import *
from config import *
from typing import final
import random

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

        from scene import score_text as __score_text__, rockets_text as __rockets_text__
        self.__score_text__ = __score_text__
        self.__rockets_text__ = __rockets_text__

        self.health = int_b(PLAYER_BASE_LIVES)
        self.rockets = int_b(PLAYER_BASE_ROCKETS)
        self.score = int_b(PLAYER_BASE_SCORE)
    
    def move(self, direction : str):
        if direction == UP:
            self.rect.y = clamp(self.rect.y - PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - self.rect.height)
        elif direction == DOWN:
            self.rect.y = clamp(self.rect.y + PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - self.rect.height)
    
    def shoot(self):
        Pew(
            self.context,
            self.rect.x + self.rect.width, 
            self.rect.y + (self.rect.height - PROJECTILE_PEW_RECT_HEIGHT) // 2, 
            TAG_PROJECTILE_PLAYER,
            RIGHT
        )
    
    def rocket(self):
        if self.rockets == 0:
            return

        self.rockets -= 1
        self.__rockets_text__.set_amount(self.rockets)

        RocketProjectile(
            self.context,
            self.rect.x + self.rect.width,
            self.rect.y + (self.rect.height - PROJECTILE_ROCKET_RECT_HEIGHT) // 2,
            TAG_PROJECTILE_PLAYER,
            RIGHT
        )
    
    def reward(self, score : int):
        self.score += score
        self.__score_text__.set_amount(self.score)
    
class Bouncy(GameObject):
    """
    Gives an object a 'bouncy movement' through `self.move()` function.<br/>
    A Bouncy object will move both horizontally and vertically between `MAP_TOP_BOUND` and `MAP_BOTTOM_BOUND`.<br/>
    The vertical direction is switched everytime the object reaches one of the vertical map bounds making the movement feel bouncy.
    """
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            width : int,
            height : int,
            tag : str,
            animations : list[Sprite],
            rect_color : tuple[int, int, int],
            horizontal_speed : int,
            vertical_speed : int,
            horizontal_direction : str,
            vertical_direction : str
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            tag = tag,
            animations = animations,
            rect_color = rect_color
        )

        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.horizontal_direction = horizontal_direction
        self.vertical_direction = vertical_direction
    
    def move(self):
        if self.horizontal_direction == LEFT:
            self.rect.x -= self.horizontal_speed
        elif self.horizontal_direction == RIGHT:
            self.rect.x += self.horizontal_speed

        if self.vertical_direction == UP:
            self.rect.y -= self.vertical_speed

            if self.rect.y <= MAP_TOP_BOUND:
                self.vertical_direction = DOWN
        elif self.vertical_direction == DOWN:
            self.rect.y += self.vertical_speed

            if self.rect.y + self.rect.height >= MAP_BOTTOM_BOUND:
                self.vertical_direction = UP

        if self.rect.x <= MAP_LEFT_BOUND - self.rect.width or self.rect.y >= MAP_RIGHT_BOUND:
            self.destroy()

class Enemy(Bouncy):
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
            vertical_direction : str,
            health : int,
            hit_reward : int,
            pop_reward : int,
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            tag = TAG_ENEMY,
            animations = animations,
            rect_color = rect_color,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            horizontal_direction = LEFT,
            vertical_direction = vertical_direction
        )

        self.last_animation_time = get_ticks()
        self.animations_interval = animations_interval

        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.vertical_direction = vertical_direction
        self.max_health = health
        self.health = health
        self.hit_reward = hit_reward
        self.pop_reward = pop_reward

        self.last_shoot_time = get_ticks()

        if DEBUG_SHOW_HEALTH_BARS:
            self.__health_bar_under = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)
            self.__health_bar_over = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)
    
    def update(self):
        super().update()

        if get_ticks() - self.last_animation_time >= self.animations_interval:
            self.animate()
            self.last_animation_time = get_ticks()
        
        self.shoot()
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
    
    def shoot(self):
        if get_ticks() - self.last_shoot_time < ENEMY_SHOOT_ROLL_INTERVAL:
            return

        roll = random.randint(1, 100)

        if roll <= ENEMY_SHOOT_CHANCE:
            Pew(
                self.context, 
                self.rect.x - self.rect.width // 4, 
                self.rect.y + (self.rect.height - PROJECTILE_PEW_RECT_HEIGHT) // 2,
                TAG_PROJECTILE_ENEMY,
                LEFT
            )

        self.last_shoot_time = get_ticks()

class Comet(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            vertical_direction : str
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
            vertical_direction = vertical_direction,
            health = COMET_HEALTH,
            hit_reward = COMET_HIT_REWARD,
            pop_reward = COMET_POP_REWARD
        )

class Shuttle(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            vertical_direction : str
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
            vertical_direction = vertical_direction,
            health = SHUTTLE_HEALTH,
            hit_reward = SHUTTLE_HIT_REWARD,
            pop_reward = SHUTTLE_POP_REWARD
        )

class Rocket(Enemy):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            horizontal_speed : int,
            vertical_speed : int,
            vertical_direction : str
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
            vertical_direction = vertical_direction,
            health = ROCKET_HEALTH,
            hit_reward = ROCKET_HIT_REWARD,
            pop_reward = SHUTTLE_POP_REWARD
        )

class Projectile(Bouncy):
    def __init__(
        self,
        context : Context,
        x : int,
        y : int,
        width : int,
        height : int,
        tag : str,
        animations : list[Sprite],
        rect_color : tuple[int, int, int],
        horizontal_speed : int,
        vertical_speed : int,
        horizontal_direction : str,
        vertical_direction : str,
        damage : int
    ):
        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            tag = tag,
            animations = animations,
            rect_color = rect_color,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            horizontal_direction = horizontal_direction,
            vertical_direction = vertical_direction
        )

        from scene import game_context, player
        self.game_context = game_context
        self.player = player

        self.horizontal_direction = horizontal_direction
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.vertical_direction = vertical_direction
        self.damage = damage
    
    def update(self):
        super().update()

        self.move()
        self.check_collisions()

    def check_collisions(self):
        if self.tag == TAG_PROJECTILE_PLAYER:
            for enemy in self.context.find_with_tags([TAG_ENEMY, TAG_PROJECTILE_ENEMY]):
                if self.collide(enemy.rect):
                    if enemy.tag == TAG_ENEMY:
                        enemy.health -= self.damage
                        self.player.reward(enemy.hit_reward)

                        if enemy.health <= 0:
                            self.player.reward(enemy.pop_reward)

                            Pop(self.context, 
                                enemy.rect.x + (enemy.rect.width - POP_RECT_WIDTH) // 2, 
                                enemy.rect.y + (enemy.rect.height - POP_RECT_HEIGHT) // 2
                            )
                            
                            enemy.destroy()
                    elif enemy.tag == TAG_PROJECTILE_ENEMY:
                        Pop(self.context, 
                            enemy.rect.x + (enemy.rect.width - POP_RECT_WIDTH) // 2, 
                            enemy.rect.y + (enemy.rect.height - POP_RECT_HEIGHT) // 2
                        )
                        
                        enemy.destroy()
                    
                    self.destroy()
        elif self.tag == TAG_PROJECTILE_ENEMY:
            pass

class Pew(Projectile):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            tag : str,
            horizontal_direction : str,
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = PROJECTILE_PEW_RECT_WIDTH,
            height = PROJECTILE_PEW_RECT_HEIGHT,
            tag = tag,
            animations = PROJECTILE_PEW_ANIMATIONS,
            rect_color = PROJECTILE_PEW_RECT_COLOR,
            horizontal_speed = PROJECTILE_PEW_HORIZONTAL_SPEED,
            vertical_speed = PROJECTILE_PEW_VERTICAL_SPEED,
            horizontal_direction = horizontal_direction,
            vertical_direction = UP,
            damage = PROJECTILE_PEW_DAMAGE
        )

class RocketProjectile(Projectile):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            tag : str,
            horizontal_direction : str,
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = PROJECTILE_ROCKET_RECT_WIDTH,
            height = PROJECTILE_ROCKET_RECT_HEIGHT,
            tag = tag,
            animations = PROJECTILE_ROCKET_ANIMATIONS,
            rect_color = PROJECTILE_ROCKET_RECT_COLOR,
            horizontal_speed = PROJECTILE_ROCKET_HORIZONTAL_SPEED,
            vertical_speed = PROJECTILE_ROCKET_VERTICAL_SPEED,
            horizontal_direction = horizontal_direction,
            vertical_direction = UP if random.randint(0, 1) == 0 else DOWN,
            damage = PROJECTILE_ROCKET_DAMAGE
        )

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
            context : Context,
            font_size : int
        ):
        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS,
            font_size = font_size
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
            context : Context,
            font_size : int
        ):

        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS,
            font_size = font_size
        )

        self.set_pos(WINDOW_WIDTH // 3 + (WINDOW_WIDTH // 3 - ROCKETS_TEXT_ABSOLUTE_WIDTH) // 2, ROCKETS_TEXT_TOP_OFFSET)
        self.set_amount(PLAYER_BASE_ROCKETS)
    
    def set_amount(self, value : int):
        value = int_b(value)

        self.set_text(">" + str(value).zfill(2))

class ScoreText(Text):
    def __init__(
            self, 
            context : Context,
            font_size : int
        ):

        super().__init__(
            context = context,
            font = FONT_SPACE_IMPACT_COUNTERS,
            font_size = font_size
        )

        self.set_amount(PLAYER_BASE_SCORE)

    def set_amount(self, value : int):
        text = str(int_b(value)).zfill(5)

        self.set_text(text)
        self.auto_pos()

    def auto_pos(self):
        self.set_pos(WINDOW_WIDTH // 3 * 2 + (WINDOW_WIDTH // 3 - self.width) // 2, SCORE_TEXT_TOP_OFFSET)