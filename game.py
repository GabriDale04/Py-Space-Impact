from utils import clamp, int_b, center_y
from pygame.time import get_ticks
from core import *
from config import *
from typing import cast
import pygame
import random

class GameManager:
    objects_tint = NOKIA_LIGHT_COLOR
    wallpaper = VOID_WALLPAPER
    game_over : bool = False

    @staticmethod
    def set_theme(theme : str, wallpaper : Sprite):
        GameManager.wallpaper = wallpaper

        if theme == NOKIA_LIGHT:
            GameManager.objects_tint = NOKIA_DARK_COLOR
        else:
            GameManager.objects_tint = NOKIA_LIGHT_COLOR

        wallpaper.tint(NOKIA_LIGHT_COLOR)

    @staticmethod
    def update():
        if GameManager.wallpaper != None:
            Window.screen.blit(GameManager.wallpaper.surface, (0, 0))

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

        self.current_tint = GameManager.objects_tint

        self.current_animation = 0
        self.animations = animations

        for animation in self.animations:
            animation.tint(self.current_tint)

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

    def on_render(self):
        super().on_render()
    
        if self.current_tint != GameManager.objects_tint:
            self.current_tint = GameManager.objects_tint

            for animation in self.animations:
                animation.tint(self.current_tint)

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

        from scene import lives_text, weapon_text, score_text, game_over_score_value_text
        self.__lives_text__ = lives_text
        self.__score_text__ = score_text
        self.__weapon_text__ = weapon_text
        self.__game_over_score_value_text__ = game_over_score_value_text

        self.current_weapon = PLAYER_DEFAULT_WEAPON

        self.lives = PLAYER_BASE_LIVES
        self.rockets = PLAYER_BASE_ROCKETS
        self.lasers = PLAYER_BASE_LASERS
        self.score = PLAYER_BASE_SCORE

        self.shield_powerup : BattleshipShield = None

        self.flight_mode = False
        self.flight_speed = 0
        self.flight_max_speed = PLAYER_FLIGHT_MAX_SPEED
        self.flight_acceleration = PLAYER_FLIGHT_ACCELERATION

        if self.current_weapon == WEAPON_ROCKET:
            self.__weapon_text__.set_amount(PLAYER_BASE_ROCKETS)
        elif self.current_weapon == WEAPON_LASER:
            self.__weapon_text__.set_amount(PLAYER_BASE_LASERS)
    
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
        self.__weapon_text__.set_amount(rockets)
    
    @property
    def lasers(self):
        return self._lasers
    
    @lasers.setter
    def lasers(self, lasers : int):
        self._lasers = lasers

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
            self.weapon()

    def move(self, direction : str):
        if direction == UP:
            self.rect.y = clamp(self.rect.y - PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - self.rect.height)
        elif direction == DOWN:
            self.rect.y = clamp(self.rect.y + PLAYER_SPEED, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - self.rect.height)
    
    def set_weapon(self, weapon : int):
        self.current_weapon = weapon

        if weapon == WEAPON_ROCKET:
            self.__weapon_text__.set_weapon(weapon, self.rockets)
        elif weapon == WEAPON_LASER:
            self.__weapon_text__.set_weapon(weapon, self.lasers)

    def shoot(self):
        Pew(
            self.context,
            self.rect.x + self.rect.width, 
            self.rect.y + (self.rect.height - PROJECTILE_PEW_RECT_HEIGHT) // 2, 
            TAG_PROJECTILE_PLAYER,
            RIGHT
        )

    def weapon(self):
        if self.current_weapon == WEAPON_ROCKET:
            self.rocket()
        elif self.current_weapon == WEAPON_LASER:
            self.laser()
    
    def rocket(self):
        if self.rockets == 0:
            return

        self.rockets -= 1
        self.__weapon_text__.set_amount(self.rockets)

        RocketProjectile(
            self.context,
            self.rect.x + self.rect.width,
            self.rect.y + (self.rect.height - PROJECTILE_ROCKET_RECT_HEIGHT) // 2,
            TAG_PROJECTILE_PLAYER,
            RIGHT
        )
    
    def laser(self):
        if self.lasers == 0:
            return
        
        self.lasers -= 1
        self.__weapon_text__.set_amount(self.lasers)

        Laser(
            self.context,
            self.rect.x + self.rect.width + self.rect.width // 4,
            self.rect.y
        )

    def fly_away(self):
        self.flight_mode = True
        self.flight_speed = 0
    
    def recall(self):
        self.rect.x = PLAYER_SPAWN_X
        self.rect.y = PLAYER_SPAWN_Y

    def damage(self):
        if self.shield_powerup != None and not self.shield_powerup.destroyed:
            return

        self.lives -= 1
        self.shield_powerup = BattleshipShield(self.context, self)
        self.recall()

        if self.lives == 0:
            self.game_over()
    
    def game_over(self):
        GameManager.game_over = True
        GameManager.set_theme(NOKIA_LIGHT, VOID_WALLPAPER)
        self.__game_over_score_value_text__.set_text(str(self.score))
    
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

class Living(Bouncy):
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
            vertical_direction : str = None,

            health : int = 0
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

        self.health = health
        self.max_health = health

        if DEBUG_SHOW_HEALTH_BARS:
            self.__health_bar_under = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)
            self.__health_bar_over = pygame.Rect(self.rect.x, self.rect.y - HEALTH_BAR_OFFSET_Y, self.rect.width, HEALTH_BAR_HEIGHT)

    def update(self):
        super().update()

        if DEBUG_SHOW_HEALTH_BARS:
            self.__debug()

    def damage(self, amount : int):
        self.health -= amount

        if self.health <= 0:
            self.pop()
    
    def pop(self):
        Pop(self.context, 
            self.rect.x + (self.rect.width - POP_RECT_WIDTH) // 2, 
            self.rect.y + (self.rect.height - POP_RECT_HEIGHT) // 2
        )

        self.destroy()

    def __debug(self):
        self.__health_bar_under.x = self.rect.x
        self.__health_bar_under.y = self.rect.y - HEALTH_BAR_OFFSET_Y
        self.__health_bar_over.x = self.rect.x
        self.__health_bar_over.y = self.rect.y - HEALTH_BAR_OFFSET_Y
        self.__health_bar_over.width = (self.health / self.max_health) * self.__health_bar_under.width

        pygame.draw.rect(Window.screen, (128, 128, 128), self.__health_bar_under)
        pygame.draw.rect(Window.screen, (255, 0, 0), self.__health_bar_over)

class Enemy(Living):
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
            shoot_chance : int
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
            vertical_direction = vertical_direction,

            health = health
        )

        from scene import player
        self.__player__ = player

        self.use_default_animator(animations_interval)

        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.vertical_direction = vertical_direction
        self.hit_reward = hit_reward
        self.pop_reward = pop_reward
        self.shoot_chance = shoot_chance

        self.last_shoot_time = get_ticks()

        self.rect.y = clamp(self.rect.y, MAP_TOP_BOUND, MAP_BOTTOM_BOUND - self.rect.height)
    
    def update(self):
        super().update()

        self.shoot()
        self.move()
        
        if self.collide(self.__player__):
            self.__player__.damage()
            self.pop()
    
    def move(self):
        super().move()
    
    def shoot(self):
        if get_ticks() - self.last_shoot_time < ENEMY_SHOOT_ROLL_INTERVAL:
            return

        roll = random.randint(1, 100)

        if roll <= self.shoot_chance:
            Pew(
                self.context, 
                self.rect.x - self.rect.width // 4, 
                self.rect.y + (self.rect.height - PROJECTILE_PEW_RECT_HEIGHT) // 2,
                TAG_PROJECTILE_ENEMY,
                LEFT
            )

        self.last_shoot_time = get_ticks()
    
    def damage(self, amount : int):
        super().damage(amount)
        
        self.__player__.score += self.hit_reward
        
        if self.destroyed:
            self.__player__.score += self.pop_reward

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
            pop_reward = COMET_POP_REWARD,
            shoot_chance = COMET_SHOOT_CHANCE
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
            pop_reward = SHUTTLE_POP_REWARD,
            shoot_chance = SHUTTLE_SHOOT_CHANCE
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
            pop_reward = VSHIP_POP_REWARD,
            shoot_chance = VSHIP_SHOOT_CHANCE
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
            pop_reward = ROCKET_POP_REWARD,
            shoot_chance = ROCKET_SHOOT_CHANCE
        )

class Acorn(Enemy):
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
            width = ACORN_RECT_WIDTH,
            height = ACORN_RECT_HEIGHT,
            animations = ACORN_ANIMATIONS,
            rect_color = ACORN_RECT_COLOR,
            animations_interval = ACORN_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = ACORN_HEALTH,
            hit_reward = ACORN_HIT_REWARD,
            pop_reward = ACORN_POP_REWARD,
            shoot_chance = ACORN_SHOOT_CHANCE
        )

class Snake(Enemy):
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
            width = SNAKE_RECT_WIDTH,
            height = SNAKE_RECT_HEIGHT,
            animations = SNAKE_ANIMATIONS,
            rect_color = SNAKE_RECT_COLOR,
            animations_interval = SNAKE_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = SNAKE_HEALTH,
            hit_reward = SNAKE_HIT_REWARD,
            pop_reward = SNAKE_POP_REWARD,
            shoot_chance = SNAKE_SHOOT_CHANCE
        )

class Drone(Enemy):
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
            width = DRONE_RECT_WIDTH,
            height = DRONE_RECT_HEIGHT,
            animations = DRONE_ANIMATIONS,
            rect_color = DRONE_RECT_COLOR,
            animations_interval = DRONE_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = DRONE_HEALTH,
            hit_reward = DRONE_HIT_REWARD,
            pop_reward = DRONE_POP_REWARD,
            shoot_chance = DRONE_SHOOT_CHANCE
        )

class Virus(Enemy):
    stop_distance = MAP_LEFT_BOUND + (WINDOW_WIDTH - MAP_LEFT_BOUND - (WINDOW_WIDTH - MAP_RIGHT_BOUND)) * (1.5 / 3)

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
            width = VIRUS_RECT_WIDTH,
            height = VIRUS_RECT_HEIGHT,
            animations = VIRUS_ANIMATIONS,
            rect_color = VIRUS_RECT_COLOR,
            animations_interval = VIRUS_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = VIRUS_HEALTH,
            hit_reward = VIRUS_HIT_REWARD,
            pop_reward = VIRUS_POP_REWARD,
            shoot_chance = VIRUS_SHOOT_CHANCE
        )

        self.has_stopped = False

    def update(self):
        super().update()

        if not self.has_stopped and self.rect.x <= Virus.stop_distance:
            self.has_stopped = True
            self.horizontal_speed = 0
            self.vertical_speed = 5
            self.shoot_chance = 100

class Cockroach(Enemy):
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
            width = COCKROACH_RECT_WIDTH,
            height = COCKROACH_RECT_HEIGHT,
            animations = COCKROACH_ANIMATIONS,
            rect_color = COCKROACH_RECT_COLOR,
            animations_interval = COCKROACH_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = COCKROACH_HEALTH,
            hit_reward = COCKROACH_HIT_REWARD,
            pop_reward = COCKROACH_POP_REWARD,
            shoot_chance = COCKROACH_SHOOT_CHANCE
        )

class BossEnemy(Enemy):    
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
            shoot_chance : int
        ):

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            animations = animations,
            rect_color = rect_color,
            animations_interval = animations_interval,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = health,
            hit_reward = hit_reward,
            pop_reward = pop_reward,
            shoot_chance=shoot_chance
        )

        self.blink_start_time = BOSS_ENEMY_DAMAGE_BLINK_DURATION
        self.blink_duration = 75

    def update(self):
        super().update()
        
        if get_ticks() - self.blink_start_time >= self.blink_duration:
            self.hidden = False

    def damage(self, amount):
        super().damage(amount)

        if not self.hidden:
            self.hidden = True
            self.blink_start_time = get_ticks()

class AlienJellyfishBoss(BossEnemy):
    stop_distance = MAP_RIGHT_BOUND - ALIEN_JELLYFISH_BOSS_RECT_WIDTH - 50

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
            pop_reward = ALIEN_JELLYFISH_BOSS_POP_REWARD,
            shoot_chance = ALIEN_JELLYFISH_BOSS_SHOOT_CHANCE
        )

        self.has_stopped = False

    def update(self):
        super().update()

        if not self.has_stopped and self.rect.x <= AlienJellyfishBoss.stop_distance:
            self.has_stopped = True
            self.horizontal_speed = 0
            self.vertical_speed = 4

class PythonBoss(BossEnemy):
    stop_distance = MAP_RIGHT_BOUND - PYTHON_BOSS_RECT_WIDTH - 50

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
            width = PYTHON_BOSS_RECT_WIDTH,
            height = PYTHON_BOSS_RECT_HEIGHT,
            animations = PYTHON_BOSS_ANIMATIONS,
            rect_color = PYTHON_BOSS_RECT_COLOR,
            animations_interval = PYTHON_BOSS_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = PYTHON_BOSS_HEALTH,
            hit_reward = PYTHON_BOSS_HIT_REWARD,
            pop_reward = PYTHON_BOSS_POP_REWARD,
            shoot_chance = PYTHON_BOSS_SHOOT_CHANCE
        )

        self.has_stopped = False

    def update(self):
        super().update()

        if not self.has_stopped and self.rect.x <= PythonBoss.stop_distance:
            self.has_stopped = True
            self.horizontal_speed = 0
            self.vertical_speed = 4

class PiranhaBoss(BossEnemy):
    stop_distance = MAP_RIGHT_BOUND - PIRANHA_BOSS_RECT_WIDTH - 50

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
            width = PIRANHA_BOSS_RECT_WIDTH,
            height = PIRANHA_BOSS_RECT_HEIGHT,
            animations = PIRANHA_BOSS_ANIMATIONS,
            rect_color = PIRANHA_BOSS_RECT_COLOR,
            animations_interval = PIRANHA_BOSS_ANIMATIONS_INTERVAL,
            horizontal_speed = horizontal_speed,
            vertical_speed = vertical_speed,
            vertical_direction = vertical_direction,
            health = PIRANHA_BOSS_HEALTH,
            hit_reward = PIRANHA_BOSS_HIT_REWARD,
            pop_reward = PIRANHA_BOSS_POP_REWARD,
            shoot_chance = PIRANHA_BOSS_SHOOT_CHANCE
        )

        self.has_stopped = False

        self.casting = False
        self.ability_position_phase = False
        self.ability_shoot_phase = False
        self.ability_last_shoot_time = 0
        self.ability_shots_done = 0
        self.ability_projectiles_distance = PIRANHA_BOSS_ABILITY_PROJECTILES_COVERED_SURFACE_HEIGHT // PIRANHA_BOSS_ABILITY_PROJECTILES_COUNT
        self.ability_shoot_pos = center_y(-self.rect.height // 2)
        self.ability_last_cast_time = get_ticks()

    def update(self):
        super().update()

        self.ability()

        if not self.has_stopped and self.rect.x <= PiranhaBoss.stop_distance:
            self.has_stopped = True
            self.horizontal_speed = 0
            self.vertical_speed = PIRANHA_BOSS_VERTICAL_SPEED_ON_STOP
            self.shoot_chance = PIRANHA_BOSS_ABILITY_SHOOT_CHANCE

    def ability(self):
        if not self.casting and get_ticks() - self.ability_last_cast_time > PIRANHA_BOSS_ABILITY_COOLDOWN:
            self.casting = True
            self.ability_position_phase = True
            self.ability_shots_done = 0
            self.vertical_speed = PIRANHA_BOSS_ABILITY_POSITION_PHASE_VERTICAL_SPEED

            if self.rect.y > self.ability_shoot_pos:
                self.vertical_direction = UP
            else:
                self.vertical_direction = DOWN      
        elif self.ability_position_phase:
            if self.vertical_direction == UP:
                self.rect.y = clamp(self.rect.y, self.ability_shoot_pos, 2147483647)
            else:
                self.rect.y = clamp(self.rect.y, -2147483648, self.ability_shoot_pos)
            
            if self.rect.y == self.ability_shoot_pos:
                self.vertical_speed = 0
                self.ability_position_phase = False
                self.ability_shoot_phase = True    
        elif self.ability_shoot_phase and get_ticks() - self.ability_last_shoot_time >= PIRANHA_BOSS_ABILITY_SHOOT_INTERVAL:
            for i in range(0, PIRANHA_BOSS_ABILITY_PROJECTILES_COUNT):
                if i == 0:
                    Pew(
                        self.context,
                        self.rect.x - 8,
                        self.rect.centery,
                        TAG_PROJECTILE_ENEMY,
                        LEFT
                    )            
                elif i % 2 == 0:
                    Pew(
                        self.context,
                        self.rect.x - 8,
                        self.rect.centery + i * self.ability_projectiles_distance,
                        TAG_PROJECTILE_ENEMY,
                        LEFT
                    )
                else:
                    Pew(
                        self.context,
                        self.rect.x - 8,
                        self.rect.centery - i * self.ability_projectiles_distance - PROJECTILE_PEW_RECT_HEIGHT * 2,
                        TAG_PROJECTILE_ENEMY,
                        LEFT
                    )

            self.ability_shots_done += 1
            self.ability_last_shoot_time = get_ticks()

            if self.ability_shots_done == PIRANHA_BOSS_ABILITY_SHOTS_COUNT:
                self.vertical_speed = PIRANHA_BOSS_VERTICAL_SPEED_ON_STOP
                self.shoot_chance = PIRANHA_BOSS_SHOOT_CHANCE
                self.ability_shoot_phase = False
                self.casting = False
                self.ability_last_cast_time = get_ticks()
    
class Projectile(Living):
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

        health : int,

        hit_damage : int,
        hit_reward : int,
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
            vertical_direction = vertical_direction,

            health = health
        )

        from scene import player
        self.__player__ = player

        self.horizontal_direction = horizontal_direction
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed
        self.vertical_direction = vertical_direction
        self.hit_damage = hit_damage
        self.hit_reward = hit_reward
        self.pop_reward = pop_reward
    
    def update(self):
        self.move()
        self.check_collisions()

    def check_collisions(self):
        if self.tag == TAG_PROJECTILE_PLAYER:
            for enemy in self.context.find_with_tags([TAG_ENEMY, TAG_PROJECTILE_ENEMY]):
                if self.collide(enemy):
                    enemy = cast(Enemy, enemy)
                    enemy.damage(self.hit_damage)

                    self.destroy()
        elif self.tag == TAG_PROJECTILE_ENEMY:
            if self.collide(self.__player__):
                self.__player__.damage()
                self.destroy()

    def damage(self, amount : int):
        super().damage(amount)

        if self.tag == TAG_PROJECTILE_ENEMY:
            self.__player__.score += self.hit_reward

            if self.destroyed:
                self.__player__.score += self.pop_reward

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

            health = PROJECTILE_PEW_HEALTH,

            hit_damage = PROJECTILE_PEW_DAMAGE,
            hit_reward = PROJECTILE_PEW_HIT_REWARD,
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

            health = PROJECTILE_ROCKET_HEALTH,

            hit_damage = PROJECTILE_ROCKET_DAMAGE,
            hit_reward = PROJECTILE_ROCKET_HIT_REWARD,
            pop_reward = PROJECTILE_ROCKET_POP_REWARD
        )

class Laser(SpaceImpactObject):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int
        ):

        self.spawn_time = get_ticks()

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = PROJECTILE_LASER_RECT_WIDTH,
            height = PROJECTILE_LASER_RECT_HEIGHT,
            animations = PROJECTILE_LASER_ANIMATIONS,
            rect_color = PROJECTILE_LASER_RECT_COLOR
        )
        
        for enemy in context.find_with_tags([TAG_ENEMY, TAG_PROJECTILE_ENEMY]):
            enemy = cast(Living, enemy)

            if self.collide(enemy):
                enemy.damage(20)
    
    def update(self):
        if get_ticks() - PROJECTILE_LASER_LIFE >= self.spawn_time:
            self.destroy()

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
            y : int,
            reward_kind : int = ROCKETS_REWARD
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

        self.reward_kind = reward_kind
        print(self.reward_kind)

        self.use_default_animator(EYE_ORB_ANIMATIONS_INTERVAL)

    def update(self):
        self.move()

        if self.collide(self.__player__):
            if self.reward_kind == ROCKETS_REWARD:
                self.__player__.rockets += EYE_ORB_ROCKETS_REWARD
                self.__player__.set_weapon(WEAPON_ROCKET)
            elif self.reward_kind == LASER_REWARD:
                self.__player__.lasers += EYE_ORB_LASERS_REWARD
                self.__player__.set_weapon(WEAPON_LASER)

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

class ThemeText(Text):
    def __init__(
            self,
            context : Context,
            font : Font,
            font_size : int
        ):

        super().__init__(
            context = context,
            font = font,
            font_size = font_size
        )

        self.current_tint = GameManager.objects_tint

        for char in self.characters:
            self.current_tint = GameManager.objects_tint
            char.sprite.tint(self.current_tint)

    def on_render(self):
        super().on_render()

        if self.current_tint != GameManager.objects_tint:
            for char in self.characters:
                self.current_tint = GameManager.objects_tint
                char.sprite.tint(self.current_tint)
    
    def set_text(self, value : str):
        super().set_text(value)

        for char in self.characters:
            char.sprite.tint(self.current_tint)

class LivesText(ThemeText):
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

class WeaponText(ThemeText):
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

        self.weapon = ">" if PLAYER_DEFAULT_WEAPON == WEAPON_ROCKET else "T"

        self.set_pos(WINDOW_WIDTH // 3 + (WINDOW_WIDTH // 3 - WEAPON_TEXT_ABSOLUTE_WIDTH) // 2, WEAPON_TEXT_TOP_OFFSET)
        self.set_amount(0)
    
    def set_amount(self, value : int):
        self.set_text(self.weapon + str(int_b(value)).zfill(2))

    def set_weapon(self, weapon : int, amount : int):
        if weapon == WEAPON_ROCKET:
            self.weapon = ">"
        elif weapon == WEAPON_LASER:
            self.weapon = "T"
        
        self.set_amount(amount)

class ScoreText(ThemeText):
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