import pygame.macosx
from utils import clamp, int_b
from pygame.time import get_ticks
from core import *
from config import *
from typing import final
import pygame
import random

class SpaceImpactObject(GameObject):
    def __init__(
            self,
            context : Context,
            x : int = 0,
            y : int = 0,
            width : int = 0,
            height : int = 0,
            tag : str = None,
            animations: list[Sprite] = [],
            rect_color : tuple[int, int, int] = (0, 0, 0)
        ):

        self.current_animation = 0
        self.animations = animations

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            tag = tag,
            sprite = animations[self.current_animation],
            rect_color = rect_color
        )

        self.default_animator = False
        self.animations_interval = -1
        self.last_animation_time = -1

    @final
    def on_render(self):
        super().on_render()
    
        if self.default_animator:
            if get_ticks() - self.last_animation_time >= self.animations_interval:
                self.animate()
                self.last_animation_time = get_ticks()

    def animate(self):
        self.current_animation = (self.current_animation + 1) % len(self.animations)
        self.sprite = self.animations[self.current_animation]

    def use_default_animator(self, animations_interval : int):
        self.default_animator = True
        self.animations_interval = animations_interval
        self.last_animation_time = get_ticks()

class Player(SpaceImpactObject):
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

        from scene import lives_text, rockets_text, score_text
        self.__lives_text__ = lives_text
        self.__score_text__ = score_text
        self.__rockets_text__ = rockets_text

        self.lives = PLAYER_BASE_LIVES
        self.rockets = PLAYER_BASE_ROCKETS
        self.score = PLAYER_BASE_SCORE

        self.shield_powerup : BattleshipShield = None

        self.flight_mode = False
        self.flight_speed = 0
        self.flight_max_speed = PLAYER_FLIGHT_MAX_SPEED
        self.flight_acceleration = PLAYER_FLIGHT_ACCELERATION
    
    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, lives : int):
        self._lives = lives
        self.__lives_text__.set_amount(lives)

    @property
    def rockets(self):
        return self._rockets

    @rockets.setter
    def rockets(self, rockets : int):
        self._rockets = rockets
        self.__rockets_text__.set_amount(rockets)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score : int):
        self._score = score
        self.__score_text__.set_amount(score)

    def update(self):
        if self.flight_mode:
            self.flight_speed = clamp(self.flight_speed + self.flight_acceleration, 0, self.flight_max_speed)
            self.rect.x += self.flight_speed
            return

        if Input.getkey(pygame.K_UP):
            self.move(UP)
        if Input.getkey(pygame.K_DOWN):
            self.move(DOWN)
        if Input.getkeydown(pygame.K_e):
            self.shoot()
        if Input.getkeydown(pygame.K_r):
            self.rocket()

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

    def fly_away(self):
        self.flight_mode = True
        self.flight_speed = 0
    
    def damage(self):
        if self.shield_powerup != None and not self.shield_powerup.destroyed:
            return

        self.shield_powerup = None
        self.lives -= 1

        if self.lives == 0:
            pass
    
class Bouncy(SpaceImpactObject):
    """
    Represents a moving object that bounces between `MAP_TOP_BOUND` and `MAP_LEFT_BOUND`.\n
    Call `self.move()` in update to make the object move every frame.\n
    Call `self.out_bounds()` to check if the object is out of the map.
    """
    def __init__(
            self,
            context : Context,
            x : int = 0,
            y : int = 0,
            width : int = 0,
            height : int = 0,
            tag : str = None,
            animations : list[Sprite] = [],
            rect_color : tuple[int, int, int] = (0, 0, 0),

            horizontal_speed : int = 0,
            vertical_speed : int = 0,
            horizontal_direction : str = None,
            vertical_direction : str = None
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

        if self.out_bounds():
            self.destroy()

    def out_bounds(self) -> bool:
        return (self.rect.x <= MAP_LEFT_BOUND - self.rect.width and self.horizontal_direction == LEFT) or \
               (self.rect.x >= MAP_RIGHT_BOUND and self.horizontal_direction == RIGHT)

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

        from scene import player
        self.__player__ = player

        self.use_default_animator(animations_interval)

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
        self.shoot()
        self.move()

        if DEBUG_SHOW_HEALTH_BARS:
            self.debug()
        
        if self.out_bounds():
            self.__player__.damage()
    
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

class VShip(Enemy):
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
            width = VSHIP_RECT_WIDTH,
            height = VSHIP_RECT_HEIGHT,
            animations = VSHIP_ANIMATIONS,
            rect_color = VSHIP_RECT_COLOR,
            animations_interval = VSHIP_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = VSHIP_HEALTH,
            hit_reward = VSHIP_HIT_REWARD,
            pop_reward = VSHIP_POP_REWARD
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
            pop_reward = ROCKET_POP_REWARD
        )

class AlienJellyfishBoss(Enemy):
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
            width = ALIEN_JELLYFISH_BOSS_RECT_WIDTH,
            height = ALIEN_JELLYFISH_BOSS_RECT_HEIGHT,
            animations = ALIEN_JELLYFISH_BOSS_ANIMATIONS,
            rect_color = ALIEN_JELLYFISH_BOSS_RECT_COLOR,
            animations_interval = ALIEN_JELLYFISH_BOSS_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = ALIEN_JELLYFISH_BOSS_HEALTH,
            hit_reward = ALIEN_JELLYFISH_BOSS_HIT_REWARD,
            pop_reward = ALIEN_JELLYFISH_BOSS_POP_REWARD
        )

    def update(self):
        super().update()

        if self.rect.x <= MAP_RIGHT_BOUND - self.rect.width - self.rect.width // 4:
            self.horizontal_speed = 0
            self.vertical_speed = 4

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
        damage : int,
        pop_reward : int
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

        from scene import player
        self.__player__ = player

        self.horizontal_direction = horizontal_direction
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.vertical_direction = vertical_direction
        self.damage = damage
        self.pop_reward = pop_reward
    
    def update(self):
        self.move()
        self.check_collisions()

    def check_collisions(self):
        if self.tag == TAG_PROJECTILE_PLAYER:
            for enemy in self.context.find_with_tags([TAG_ENEMY, TAG_PROJECTILE_ENEMY]):
                if self.collide(enemy):
                    if enemy.tag == TAG_ENEMY:
                        enemy.health -= self.damage
                        self.__player__.score += enemy.hit_reward

                        if enemy.health <= 0:
                            self.__player__.score += enemy.pop_reward

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
                        
                        self.__player__.score += enemy.pop_reward
                        enemy.destroy()
                    
                    self.destroy()
        elif self.tag == TAG_PROJECTILE_ENEMY:
            if self.collide(self.__player__):
                self.__player__.damage()
                self.destroy()

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

            damage = PROJECTILE_PEW_DAMAGE,
            pop_reward = PROJECTILE_PEW_POP_REWARD
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

            damage = PROJECTILE_ROCKET_DAMAGE,
            pop_reward = PROJECTILE_ROCKET_POP_REWARD
        )

class Pop(SpaceImpactObject):
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

        self.use_default_animator(self.animations_interval)

    def update(self):
        if get_ticks() - self.spawn_time >= POP_DURATION:
            self.destroy()

class EyeOrb(Bouncy):
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
            width = EYE_ORB_RECT_WIDTH,
            height = EYE_ORB_RECT_HEIGHT,
            animations = EYE_ORB_ANIMATIONS,
            rect_color = EYE_ORB_RECT_COLOR,

            horizontal_speed = EYE_ORB_HORIZONTAL_SPEED,
            vertical_speed= EYE_ORB_VERTICAL_SPEED,
            horizontal_direction = LEFT,
            vertical_direction = UP
        )

        from scene import player
        self.__player__ = player

        self.use_default_animator(EYE_ORB_ANIMATIONS_INTERVAL)

    def update(self):
        self.move()

        if self.collide(self.__player__):
            self.__player__.rockets += EYE_ORB_ROCKETS_REWARD
            self.destroy()

class BattleshipShield(SpaceImpactObject):
    def __init__(
            self,
            context : Context,
            owner : SpaceImpactObject
        ):

        super().__init__(
            context = context,
            x = 0,
            y = 0,
            width = BATTLE_SHIP_SHIELD_RECT_WIDTH,
            height = BATTLE_SHIP_SHIELD_RECT_HEIGHT,
            animations = BATTLE_SHIP_SHIELD_ANIMATIONS,
            rect_color = BATTLE_SHIP_SHIELD_RECT_COLOR
        )

        self.use_default_animator(BATTLE_SHIP_SHIELD_ANIMATIONS_INTERVAL)
        self.owner = owner
        self.start_time = get_ticks()
    
    def update(self):
        self.rect.center = self.owner.rect.center

        if get_ticks() - self.start_time >= BATTLE_SHIP_SHIELD_DURATION:
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
        self.set_text(">" + str(int_b(value)).zfill(2))

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