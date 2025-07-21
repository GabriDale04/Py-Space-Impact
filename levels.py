import random
from core import *
from config import *
from utils import random_y, random_vertical_direction, args
from pygame.time import get_ticks
from game import Enemy, Comet, Shuttle, VShip, Rocket
from scene import game_context

class Wave:
    def __init__(self):
        self.enemies : list[dict] = []
        self.current_enemy : int = 0
        self.last_spawn_time = None

    def start(self):
        self.last_spawn_time = get_ticks()

    def update(self):
        if self.last_spawn_time == None:
            return

        if self.current_enemy < len(self.enemies) and get_ticks() - self.last_spawn_time >= self.enemies[self.current_enemy]["delay"]:
            self.spawn(self.enemies[self.current_enemy])
            self.current_enemy += 1
            self.last_spawn_time = get_ticks()
    
    def spawn(self, enemy : dict):
        Enemy_cls = enemy["enemy"]
        Enemy_cls(**enemy["arguments"])

    def after(self, delay : int, enemy_cls : type[Enemy], **arguments) -> 'Wave':
        self.enemies.append({
            "delay": delay,
            "enemy": enemy_cls,
            "arguments": arguments
        })

        return self
    
    @staticmethod
    def build(delays : list[int], enemies_cls : list[type[Enemy]], arguments) -> 'Wave':
        wave = Wave()

        for i in range(0, len(enemies_cls)):
            Enemy_cls = enemies_cls[i]

            wave.after(delays[i], Enemy_cls, **arguments)
        
        return wave

class Level:
    def __init__(self):
        self.waves : list[dict] = []
        self.current_wave : int = 0
        self.last_wave_time = get_ticks()

        self.started_waves : list[Wave] = []
    
    def update(self):
        if self.current_wave < len(self.waves) and get_ticks() - self.last_wave_time >= self.waves[self.current_wave]["delay"]:
            wave : Wave = self.waves[self.current_wave]["wave"]
            wave.start()
            self.started_waves.append(wave)

            self.current_wave += 1
            self.last_wave_time = get_ticks()

        for wave in self.started_waves:
            wave.update()

    def after(self, delay : int, wave : Wave) -> 'Level':
        self.waves.append({
            "delay": delay,
            "wave": wave
        })

        return self

def wave_args_builder(min_hspeed : int, max_hspeed : int, min_vspeed : int, max_vspeed : int, y : int = None, vertical_dir : str = None):
    if y == None:
        y = random_y()
    if vertical_dir == None:
        vertical_dir = random_vertical_direction()

    return args(
        context=game_context,
        x=MAP_RIGHT_BOUND,
        y=y,
        horizontal_speed=random.randint(min_hspeed, max_hspeed),
        vertical_speed=random.randint(min_vspeed, max_vspeed),
        vertical_direction=random_vertical_direction()
    )

def level1() -> Level:
    WAVE1_DELAYS = [0, 1250, 1250]
    WAVE1_ENEMIES = [Comet, Comet, Comet]
    WAVE1_MIN_HORIZONTAL_SPEED = 2
    WAVE1_MAX_HORIZONTAL_SPEED = 3
    WAVE1_MIN_VERTICAL_SPEED = 1
    WAVE1_MAX_VERTICAL_SPEED = 2
    WAVE1_ARGS = wave_args_builder(WAVE1_MIN_HORIZONTAL_SPEED, WAVE1_MAX_HORIZONTAL_SPEED, WAVE1_MIN_VERTICAL_SPEED, WAVE1_MAX_VERTICAL_SPEED)

    WAVE2_DELAYS = [0, 1250, 1250]
    WAVE2_ENEMIES = [Shuttle, Shuttle, Shuttle]
    WAVE2_MIN_HORIZONTAL_SPEED = 2
    WAVE2_MAX_HORIZONTAL_SPEED = 3
    WAVE2_MIN_VERTICAL_SPEED = 1
    WAVE2_MAX_VERTICAL_SPEED = 2
    WAVE2_ARGS = wave_args_builder(WAVE2_MIN_HORIZONTAL_SPEED, WAVE2_MAX_HORIZONTAL_SPEED, WAVE2_MIN_VERTICAL_SPEED, WAVE2_MAX_VERTICAL_SPEED)

    WAVE3_DELAYS = [0, 1250, 1250]
    WAVE3_ENEMIES = [VShip, VShip, VShip]
    WAVE3_MIN_HORIZONTAL_SPEED = 2
    WAVE3_MAX_HORIZONTAL_SPEED = 3
    WAVE3_MIN_VERTICAL_SPEED = 1
    WAVE3_MAX_VERTICAL_SPEED = 2
    WAVE3_ARGS = wave_args_builder(WAVE3_MIN_HORIZONTAL_SPEED, WAVE3_MAX_HORIZONTAL_SPEED, WAVE3_MIN_VERTICAL_SPEED, WAVE3_MAX_VERTICAL_SPEED)

    WAVE4_DELAYS = [0, 1250, 1250]
    WAVE4_ENEMIES = [Rocket, Rocket, Rocket]
    WAVE4_MIN_HORIZONTAL_SPEED = 3
    WAVE4_MAX_HORIZONTAL_SPEED = 4
    WAVE4_MIN_VERTICAL_SPEED = 1
    WAVE4_MAX_VERTICAL_SPEED = 1
    WAVE4_ARGS = wave_args_builder(WAVE4_MIN_HORIZONTAL_SPEED, WAVE4_MAX_HORIZONTAL_SPEED, WAVE4_MIN_VERTICAL_SPEED, WAVE4_MAX_VERTICAL_SPEED)

    return Level().after(
        2000,
        Wave.build(WAVE1_DELAYS, WAVE1_ENEMIES, WAVE1_ARGS)
    ).after(
        5000,
        Wave.build(WAVE2_DELAYS, WAVE2_ENEMIES, WAVE2_ARGS)
    ).after(
        5000,
        Wave.build(WAVE3_DELAYS, WAVE3_ENEMIES, WAVE3_ARGS)
    ).after(
        5000,
        Wave.build(WAVE4_DELAYS, WAVE4_ENEMIES, WAVE4_ARGS)
    )