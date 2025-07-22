import random
from core import *
from config import *
from utils import random_y, random_vertical_direction, args
from pygame.time import get_ticks
from game import EyeOrb, SpaceImpactObject, Comet, Shuttle, VShip, Rocket
from scene import game_context

class Wave:
    def __init__(
            self,
            spawn_delay : int,
            wave_size : int,
            entity_cls : type[SpaceImpactObject],
            **cls_args
        ):

        self.spawn_delay = spawn_delay
        self.wave_size = wave_size
        self.entity_cls = entity_cls
        self.cls_args = cls_args

        self.started = False
        self.cleared = False
        self.spawned_entities : list[SpaceImpactObject] = []
        self.spawned_count = 0
        self.last_spawn_time = None
    
    def start(self):
        if not self.started:
            self.last_spawn_time = get_ticks() - self.spawn_delay
            self.started = True

    def update(self):
        if self.last_spawn_time == None or self.cleared:
            return

        if self.spawned_count != self.wave_size and get_ticks() - self.last_spawn_time >= self.spawn_delay:
            entity = self.entity_cls(**self.cls_args)
            self.spawned_entities.append(entity)
            self.spawned_count += 1
            self.last_spawn_time = get_ticks()

        if self.spawned_count == self.wave_size:
            self.cleared = all(entity.destroyed for entity in self.spawned_entities)

class Level:
    def __init__(self, boss_cls : type[SpaceImpactObject], **cls_args):
        self.waves : list[dict] = []
        self.boss_cls = boss_cls
        self.cls_args = cls_args
        
        self.cleared = False
        self.current_wave = 0
        self.last_wave_time = None
    
    def start(self):
        self.last_wave_time = get_ticks()

    def update(self):
        if self.last_wave_time == None or self.cleared:
            return

        if self.current_wave < len(self.waves) and get_ticks() - self.last_wave_time >= self.waves[self.current_wave]["delay"]:
            wave : Wave = self.waves[self.current_wave]["wave"]
            wave.start()

            self.current_wave += 1
            self.last_wave_time = get_ticks()

        for wave_dict in self.waves:
            wave : Wave = wave_dict["wave"]

            if not wave.cleared and wave.started:
                wave.update()
    
    def after(self, delay : int, wave : Wave) -> 'Level':
        self.waves.append({
            "delay": delay,
            "wave": wave
        })

        return self

def makeargs_any(y : int = -1, **kwArgs):
    if y == -1:
        y = random_y()

    return args(context=game_context, x=MAP_RIGHT_BOUND, y=y, **kwArgs)

def makeargs_enemy(hspeed_min : int, hspeed_max : int, vspeed_min : int, vspeed_max : int, y : int = -1, vdir : str = -1):
    if vdir == -1:
        vdir = random_vertical_direction()
    
    hspeed = random.randint(hspeed_min, hspeed_max)
    vspeed = random.randint(vspeed_min, vspeed_max)

    return makeargs_any(y=y, horizontal_speed=hspeed, vertical_speed=vspeed, vertical_direction=vdir)

level1 = Level(None).after(
    2000,
    Wave(1000, 3, Comet, **makeargs_enemy(2, 2, 2, 2))
).after(
    7000,
    Wave(1000, 3, Shuttle, **makeargs_enemy(2, 2, 2, 2))
).after(
    7000,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 2, 2, 2))
).after(
    7000,
    Wave(1000, 3, Rocket, **makeargs_enemy(4, 4, 1, 1))
).after(
    7000,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 2, 1, 1))
).after(
    3250,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 2, 1, 1))
).after(
    500,
    Wave(0, 1, EyeOrb, **makeargs_any())
)

#level1 = Level().after(0, Wave(0, 1, EyeOrb, **makeargs_any()))