import random
from core import *
from config import *
from utils import random_y, random_vertical_direction, args, center_x
from pygame.time import get_ticks
from game import *
from scene import *

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
        if self.cleared or self.last_spawn_time == None:
            return

        if self.spawned_count != self.wave_size and get_ticks() - self.last_spawn_time >= self.spawn_delay:
            entity = self.entity_cls(**self.cls_args)
            self.spawned_entities.append(entity)
            self.spawned_count += 1
            self.last_spawn_time = get_ticks()

        if self.spawned_count == self.wave_size:
            self.cleared = all(entity.destroyed for entity in self.spawned_entities)

class Level:
    def __init__(self, theme : str, wallpaper : Sprite, boss_cls : type[SpaceImpactObject], **cls_args):
        self.waves : list[dict] = []
        self.theme = theme
        self.wallpaper = wallpaper
        self.boss_cls = boss_cls
        self.cls_args = cls_args
        
        self.started = False
        self.cleared = False
        self.current_wave = 0
        self.last_wave_time = None
        self.is_boss_stage = False
        self.boss : SpaceImpactObject = None
    
    def start(self):
        if not self.started:
            self.started = True
            self.last_wave_time = get_ticks()
            GameManager.set_theme(self.theme, self.wallpaper)

    def update(self):
        spawn_boss = True

        for wave_dict in self.waves:
            wave : Wave = wave_dict["wave"]

            if not wave.cleared:
                if wave_dict["requires_clear"]:
                    spawn_boss = False

                if wave.started:
                    wave.update()

        if self.current_wave < len(self.waves) and get_ticks() - self.last_wave_time >= self.waves[self.current_wave]["delay"]:
            wave : Wave = self.waves[self.current_wave]["wave"]
            wave.start()

            self.current_wave += 1
            self.last_wave_time = get_ticks()

        if self.is_boss_stage:
            self.cleared = self.boss.destroyed
            return

        if self.last_wave_time == None:
            return
        
        if spawn_boss:
            self.is_boss_stage = True
            self.boss = self.boss_cls(**self.cls_args)

    def after(self, delay : int, wave : Wave, requires_clear = True) -> 'Level':
        self.waves.append({
            "delay": delay,
            "wave": wave,
            "requires_clear": requires_clear
        })

        return self
    
    def skip(self, num : int) -> 'Level':
        """
        This removes, starting from the first element, the specified number of waves.\n
        Useful for debugging.
        """
        while num > 0 or len(self.waves) == 0:
            self.waves.pop(0)
            num -= 1

        return self

class LevelManager:
    def __init__(self, levels : list[Level]):
        self.levels = levels
        self.current_level : Level = None
        self.current_level_index = 0
    
    def update(self):
        current_level = self.levels[self.current_level_index]

        if not current_level.started:
           current_level.start()
           self.current_level = current_level
        elif not player.flight_mode and current_level.cleared:
            player.fly_away()
            
            for projectile in game_context.find_with_tags([TAG_PROJECTILE_ENEMY, TAG_PROJECTILE_PLAYER]):
                projectile.vertical_speed = 0
        # When the player has flew at least three 'windows', go to next level
        elif player.flight_mode and player.rect.x >= WINDOW_WIDTH * 3:
            player.flight_mode = False
            self.current_level_index += 1

            if self.current_level_index >= len(self.levels):
                player.game_over()
            else:
                player.recall()

                for projectile in game_context.find_with_tags([TAG_PROJECTILE_ENEMY, TAG_PROJECTILE_PLAYER]):
                    projectile.destroy()

        current_level.update()


def makeargs_any(y : int = -1, **kwArgs):
    if y == -1:
        y = random_y()

    return args(context=game_context, x=MAP_RIGHT_BOUND, y=y, **kwArgs)

def makeargs_enemy(hspeed_min : int, hspeed_max : int, vspeed_min : int, vspeed_max : int, y : int = -1, vdir : str = None, **otherArgs):
    if vdir == None:
        vdir = random_vertical_direction()
    
    hspeed = random.randint(hspeed_min, hspeed_max)
    vspeed = random.randint(vspeed_min, vspeed_max)

    return makeargs_any(y=y, horizontal_speed=hspeed, vertical_speed=vspeed, vertical_direction=vdir, **otherArgs)

level1 = Level(NOKIA_DARK, VOID_WALLPAPER, AlienJellyfishBoss, **makeargs_enemy(3, 3, 5, 5, MAP_TOP_BOUND, DOWN)).after(
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
    7000,
    Wave(0, 1, Shuttle, **makeargs_enemy(3, 5, 1, 1))
).after(
    3000,
    Wave(1000, 2, Shuttle, **makeargs_enemy(3, 3, 2, 3))
).after(
    4000,
    Wave(1000, 3, Comet, **makeargs_enemy(3, 3, 1, 1))
).after(
    2000,
    Wave(0, 1, EyeOrb, **makeargs_any()),
    requires_clear=False
)

level2 = Level(NOKIA_LIGHT, SKY_WALLPAPER, PythonBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN)).after(
    1000,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 2, 1, 1, y=MAP_TOP_BOUND + 100, vdir=DOWN))
).after(
    0,
    Wave(1000, 3, VShip, **makeargs_enemy(2, 2, 1, 1, y=MAP_BOTTOM_BOUND - 100 - VSHIP_RECT_HEIGHT, vdir=UP))
).after(
    3250,
    Wave(0, 1, EyeOrb, **makeargs_any()),
    requires_clear=False
).after(
    4000,
    Wave(1000, 3, Acorn, **makeargs_enemy(2, 2, 1, 1, y=MAP_TOP_BOUND + 100, vdir=UP))
).after(
    0,
    Wave(1000, 3, Acorn, **makeargs_enemy(2, 2, 1, 1, y=MAP_BOTTOM_BOUND - 100 - ACORN_RECT_HEIGHT, vdir=UP))
).after(
    5000,
    Wave(0, 1, Shuttle, **makeargs_enemy(2, 5, 1, 2))
).after(
    1000,
    Wave(0, 1, Shuttle, **makeargs_enemy(2, 5, 1, 2))
).after(
    1000,
    Wave(0, 1, Shuttle, **makeargs_enemy(2, 5, 1, 2))
).after(
    2500,
    Wave(1000, 3, Shuttle, **makeargs_enemy(3, 3, 1, 1))
).after(
    4000,
    Wave(1000, 3, Rocket, **makeargs_enemy(4, 4, 1, 1))
).after(
    4000,
    Wave(0, 1, Rocket, **makeargs_enemy(4, 4, 1, 1))
).after(
    1000,
    Wave(0, 1, Rocket, **makeargs_enemy(4, 4, 1, 1))
).after(
    4000,
    Wave(2500, 5, Rocket, **makeargs_enemy(4, 4, 1, 1))
)

level3 = Level(NOKIA_LIGHT, MOUNTAINS_WALLPAPER, PiranhaBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN)).after(
    1000,
    Wave(1250, 6, Snake, **makeargs_enemy(1, 1, 1, 1))
).after(
    7500,
    Wave(1250, 4, Snake, **makeargs_enemy(1, 1, 1, 1))
).after(
    3000,
    Wave(500, 3, Acorn, **makeargs_enemy(8, 10, 0, 0))
).after(
    2000,
    Wave(0, 1, EyeOrb, **makeargs_any())
).after(
    4000,
    Wave(1000, 3, Comet, **makeargs_enemy(2, 4, 1, 2))
).after(
    2000,
    Wave(1000, 3, Comet, **makeargs_enemy(2, 4, 1, 2))
).after(
    4000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_TOP_BOUND + 25))
).after(
    0,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_BOTTOM_BOUND - 25 - DRONE_RECT_HEIGHT))
).after(
    2500,
    Wave(0, 1, Virus, **makeargs_enemy(2, 2, 0, 0, y=center_y(-VIRUS_RECT_HEIGHT // 2), horizontal_stop_distance=center_x(-VIRUS_RECT_WIDTH // 2)))
)

level4 = Level(NOKIA_LIGHT, CITY_WALLPAPER, YotsuBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN)).after(
    2000,
    Wave(1000, 5, Cockroach, **makeargs_enemy(3, 3, 0, 0))
).after(
    6000,
    Wave(1000, 5, Cockroach, **makeargs_enemy(3, 3, 2, 2))
).after(
    6000,
    Wave(1000, 3, Rocket, **makeargs_enemy(2, 3, 1, 2))
).after(
    4000,
    Wave(0, 1, Rocket, **makeargs_enemy(3, 4, 1, 1))
).after(
    3000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_TOP_BOUND))
).after(
    1000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=center_y(-DRONE_RECT_HEIGHT // 2)))
).after(
    1000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_BOTTOM_BOUND - DRONE_RECT_HEIGHT))
).after(
    3000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_TOP_BOUND))
).after(
    1000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=MAP_BOTTOM_BOUND - DRONE_RECT_HEIGHT))
).after(
    1000,
    Wave(0, 1, Drone, **makeargs_enemy(2, 2, 0, 0, y=center_y(-DRONE_RECT_HEIGHT // 2)))
).after(
    1000,
    Wave(0, 1, EyeOrb, **makeargs_any(reward_kind=LASER_REWARD))
).after(
    4500,
    Wave(1000, 5, Cockroach, **makeargs_enemy(3, 4, 2, 3))
)

level5 = Level(NOKIA_DARK, CURSED_WALLPAPER, PufferfishBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN)).after(
    1000,
    Wave(1000, 4, Bean, **makeargs_enemy(3, 4, 3, 4))
).after(
    5000,
    Wave(650, 5, Bean, **makeargs_enemy(5, 5, 0, 0))    
).after(
    2500,
    Wave(0, 1, Virus, **makeargs_enemy(2, 2, 0, 0, y=center_y(-VIRUS_RECT_HEIGHT // 2), horizontal_stop_distance=center_x(-VIRUS_RECT_WIDTH // 2)))
).after(
    8000,
    Wave(0, 1, EyeOrb, **makeargs_any(), reward_kind=HEALTH_REWARD),
    requires_clear=False
).after(
    1000,
    Wave(1000, 5, Snake, **makeargs_enemy(4, 4, 3, 5))
).after(
    6000,
    Wave(0, 1, Comet, **makeargs_enemy(6, 6, 0, 0, y=center_y(-COMET_RECT_HEIGHT // 2)))
).after(
    1000,
    Wave(0, 1, Comet, **makeargs_enemy(6, 6, 0, 0, y=center_y(-MAP_GAME_FIELD_HEIGHT // 3)))
).after(
    0,
    Wave(0, 1, Comet, **makeargs_enemy(6, 6, 0, 0, y=center_y(MAP_GAME_FIELD_HEIGHT // 3 - COMET_RECT_WIDTH // 2)))
).after(
    1000,
    Wave(0, 1, Comet, **makeargs_enemy(6, 6, 0, 0, y=center_y(-COMET_RECT_HEIGHT // 2)))
).after(
    3000,
    Wave(1000, 5, VShip, **makeargs_enemy(3, 3, 1, 1, y=MAP_TOP_BOUND, health=3, horizontal_stop_distance=center_x(-VSHIP_RECT_WIDTH // 2), vertical_stop_speed=2))
).after(
    0,
    Wave(1000, 5, VShip, **makeargs_enemy(3, 3, 1, 1, y=MAP_BOTTOM_BOUND, health=3, horizontal_stop_distance=center_x(-VSHIP_RECT_WIDTH // 2), vertical_stop_speed=2)) 
).after(
    8000,
    Wave(1000, 6, Shuttle, **makeargs_enemy(4, 4, 6, 6))
).after(
    7000,
    Wave(1000, 4, Shuttle, **makeargs_enemy(2, 3, 3, 4))
).after(
    5000,
    Wave(0, 1, Shuttle, **makeargs_enemy(2, 2, 2, 2, health=30, horizontal_stop_distance=center_x(-VSHIP_RECT_WIDTH // 2))) 
)

level6 = Level(NOKIA_DARK, CURSED2_WALLPAPER, ShellBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN))

level7 = Level(NOKIA_LIGHT, ROAD_WALLPAPER, SquidBoss, **makeargs_enemy(3, 3, 3, 3, MAP_TOP_BOUND, DOWN))

level8 = Level(NOKIA_LIGHT, ROAD2_WALLPAPER, KrakenBoss, **makeargs_enemy(2, 2, 0, 0, y=center_y(-KRAKEN_BOSS_RECT_WIDTH // 2), horizontal_stop_distance=KRAKEN_BOSS_RECT_WIDTH))

level_test = Level(NOKIA_LIGHT, ROAD2_WALLPAPER, KrakenBoss, **makeargs_enemy(2, 2, 0, 0, y=center_y(-KRAKEN_BOSS_RECT_WIDTH // 2), horizontal_stop_distance=KRAKEN_BOSS_RECT_WIDTH)).after(
    0,
    Wave(0, 1, EyeOrb, **makeargs_any(y=MAP_BOTTOM_BOUND, reward_kind=LASER_REWARD)),
    requires_clear=False
).after(
    0,
    Wave(1000, 5, Star, **makeargs_enemy(2, 2, 2, 2)) 
)

level_manager = LevelManager([level1, level2, level3, level4, level5, level6, level7, level8])
level_manager = LevelManager([level8])