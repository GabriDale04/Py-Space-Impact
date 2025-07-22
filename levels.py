import random
from core import *
from config import *
from utils import random_y, random_vertical_direction, args
from pygame.time import get_ticks
from game import SpaceImpactObject, Comet, Shuttle, VShip, Rocket
from scene import game_context

class Wave:
    def __init__(
            self,
            spawn_delay : int,
            wave_size : int,
            entity_cls : type[SpaceImpactObject],
            **arguments
        ):

        self.spawn_delay = spawn_delay
        self.wave_size = wave_size
        self.entity_cls = entity_cls
        self.arguments = arguments

        self.cleared = False
        self.spawned_entities : list[SpaceImpactObject] = []
        self.spawned_count = 0
        self.last_spawn_time = None
    
    def start(self):
        self.last_spawn_time = get_ticks() - self.spawn_delay

    def update(self):
        if self.last_spawn_time == None or self.cleared:
            return

        if self.spawned_count != self.wave_size and get_ticks() - self.last_spawn_time >= self.spawn_delay:
            entity = self.entity_cls(**self.arguments)
            self.spawned_entities.append(entity)
            self.spawned_count += 1
            self.last_spawn_time = get_ticks()

        for entity in self.spawned_entities:
            if not entity.destroyed:
                return

class Level:
    def __init__(self):
        self.waves : list[dict] = []
        
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

        new_wave_list : list[dict] = []

        for wave_dict in self.waves:
            wave : Wave = wave_dict["wave"]

            if not wave.cleared:
                wave.update()
                new_wave_list.append(wave_dict)
        
        self.waves = new_wave_list
        
        if len(self.waves) == 0:
            self.cleared = True
    
    def after(self, delay : int, wave : Wave) -> 'Level':
        self.waves.append({
            "delay": delay,
            "wave": wave
        })

        return self

def makeargs_enemy(hspeed_min : int, hspeed_max : int, vspeed_min : int, vspeed_max : int, y : int = -1, vdir : str = -1):
    if y == -1:
        y = random_y()
    if vdir == -1:
        vdir = random_vertical_direction()
    
    hspeed = random.randint(hspeed_min, hspeed_max)
    vspeed = random.randint(vspeed_min, vspeed_max)

    return args(context=game_context, x=MAP_RIGHT_BOUND, y=y, horizontal_speed=hspeed, vertical_speed=vspeed, vertical_direction=vdir)

level1 = Level().after(
    2000,
    Wave(1000, 3, Comet, **makeargs_enemy(2, 3, 2, 2))
).after(
    5000,
    Wave(1000, 3, Shuttle, **makeargs_enemy(2, 3, 2, 2))
).after(
    5000,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 3, 2, 2))
).after(
    5000,
    Wave(1000, 3, Rocket, **makeargs_enemy(3, 4, 1, 1))
)