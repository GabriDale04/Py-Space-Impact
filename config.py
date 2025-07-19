from core import Sprite, TextureAtlas, Font, Text

# CONFIGURATION FILE FOR Py-Space-Impact
# Edit anything you like
# DO NOT DELETE OR RENAME VARIABLES, WILL CRASH

WINDOW_WIDTH = 1124
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Space Impact"

MAP_VERTICAL_BOUND_OFFSET = 100
MAP_HORIZONTAL_BOUND_OFFSET = 0
MAP_TOP_BOUND = WINDOW_HEIGHT - (WINDOW_HEIGHT - MAP_VERTICAL_BOUND_OFFSET)
MAP_BOTTOM_BOUND = WINDOW_HEIGHT - MAP_VERTICAL_BOUND_OFFSET
MAP_LEFT_BOUND = WINDOW_WIDTH - (WINDOW_WIDTH - MAP_HORIZONTAL_BOUND_OFFSET)
MAP_RIGHT_BOUND = WINDOW_WIDTH - MAP_HORIZONTAL_BOUND_OFFSET

BATTLE_SHIP_RECT_WIDTH = 10 * 12
BATTLE_SHIP_RECT_HEIGHT = 7 * 12
BATTLE_SHIP_RECT_COLOR = (0, 100, 0)
BATTLE_SHIP_ANIMATIONS = [Sprite.load("textures/battleship.png", 144, 144)]

COMET_RECT_WIDTH = 10 * 12
COMET_RECT_HEIGHT = 5 * 12
COMET_RECT_COLOR = (255, 0, 0)
COMET_ANIMATIONS = [Sprite.load("textures/comet1.png", 144, 144), Sprite.load("textures/comet2.png", 144, 144)]
COMET_ANIMATIONS_INTERVAL = 100
COMET_HEALTH = 1

SHUTTLE_RECT_WIDTH = 8 * 12
SHUTTLE_RECT_HEIGHT = 5 * 12
SHUTTLE_RECT_COLOR = (255, 0, 0)
SHUTTLE_ANIMATIONS = [Sprite.load("textures/shuttle1.png", 144, 144), Sprite.load("textures/shuttle2.png", 144, 144), Sprite.load("textures/shuttle3.png", 144, 144)]
SHUTTLE_ANIMATIONS_INTERVAL = 100
SHUTTLE_HEALTH = 1

ROCKET_RECT_WIDTH = 10 * 12
ROCKET_RECT_HEIGHT = 5 * 12
ROCKET_RECT_COLOR = (255, 0, 0)
ROCKET_ANIMATIONS = [Sprite.load("textures/rocket1.png", 144, 144), Sprite.load("textures/rocket2.png", 144, 144)]
ROCKET_ANIMATIONS_INTERVAL = 100
ROCKET_HEALTH = 3

PROJECTILE_RECT_WIDTH = 3 * 12
PROJECTILE_RECT_HEIGHT = 1 * 12
PROJECTILE_RECT_COLOR = (210, 112, 90)
PROJECTILE_ANIMATIONS = [Sprite.load("textures/projectile.png", 144, 144)]
PROJECTILE_SPEED = 3
PROJECTILE_DAMAGE = 1

POP_RECT_WIDTH = 5 * 12
POP_RECT_HEIGHT = 5 * 12
POP_RECT_COLOR = (0, 100, 0)
POP_ANIMATIONS = [Sprite.load("textures/pop1.png", 144, 144), Sprite.load("textures/pop2.png", 144, 144)]
POP_DURATION = 100

PLAYER_SPAWN_X = 25
PLAYER_SPAWN_Y = MAP_TOP_BOUND
PLAYER_SPEED = 5
PLAYER_BASE_LIVES = 3
PLAYER_BASE_SCORE = 0x7FFFFFFF
PLAYER_BASE_ROCKETS = 3

UP = "up"
LEFT = "left"
RIGHT = "right"
DOWN = "down"

TAG_ENEMY = "enemy"
TAG_PROJECTILE_PLAYER = "projectile_player"
TAG_PROJECTILE_ENEMY = "projectile_enemy"

FONT_RECT_COLOR = (255, 192, 203)

FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_WIDTH = 8 * 3
FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_HEIGHT = 5 * 3
FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_GAP = 1 * 3
FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS = TextureAtlas(
    "textures/fonts/space_impact_counters.png", 
    FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_WIDTH, 
    FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_HEIGHT, 
    FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_GAP
)
FONT_SPACE_IMPACT_COUNTERS_CHAR_SPRITE_WIDTH = 8 * 3 * 4
FONT_SPACE_IMPACT_COUNTERS_CHAR_SPRITE_HEIGHT = 5 * 3 * 4 
FONT_SPACE_IMPACT_COUNTERS_CHAR_GAP = FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS_CHAR_GAP * 4
FONT_SPACE_IMPACT_COUNTERS_CHAR_MAP = {
    "0": {
        "coords": (0, 0),
        "size": (36, 60)
    },
    "1": {
        "coords": (1, 0),
        "size": (36, 60)
    },
    "2": {
        "coords": (2, 0),
        "size": (36, 60)
    },
    "3": {
        "coords": (3, 0),
        "size": (36, 60)
    },
    "4": {
        "coords": (0, 1),
        "size": (36, 60)
    },
    "5": {
        "coords": (1, 1),
        "size": (36, 60)
    },
    "6": {
        "coords": (2, 1),
        "size": (36, 60)
    },
    "7": {
        "coords": (3, 1),
        "size": (36, 60)
    },
    "8": {
        "coords": (0, 2),
        "size": (36, 60)
    },
    "9": {
        "coords": (1, 2),
        "size": (36, 60)
    },
    "v": {
        "coords": (2, 2),
        "size": (60, 60)
    },
    ">": {
        "coords": (3, 2),
        "size": (64, 60)
    },
    "-": {
        "coords": (0, 3),
        "size": (36, 60)
    }
}

FONT_SPACE_IMPACT_COUNTERS = Font(
    FONT_SPACE_IMPACT_COUNTERS_TEXTURE_ATLAS, 
    FONT_SPACE_IMPACT_COUNTERS_CHAR_MAP, 
    FONT_SPACE_IMPACT_COUNTERS_CHAR_SPRITE_WIDTH,
    FONT_SPACE_IMPACT_COUNTERS_CHAR_SPRITE_HEIGHT,
    FONT_SPACE_IMPACT_COUNTERS_CHAR_GAP
)

LIVES_TEXT_ABSOLUTE_WIDTH = Text.width_of("vvv", FONT_SPACE_IMPACT_COUNTERS_CHAR_MAP, FONT_SPACE_IMPACT_COUNTERS_CHAR_GAP)
ROCKETS_TEXT_ABSOLUTE_WIDTH = Text.width_of(">00", FONT_SPACE_IMPACT_COUNTERS_CHAR_MAP, FONT_SPACE_IMPACT_COUNTERS_CHAR_GAP)

# Tells the game to use 16bit numbers for counters such as score, health and rockets. If False, uses 32bit integers
USE_16BIT_INTEGERS = False
FREEZE_SCORE_ON_OVERFLOW = True
DEBUG_SHOW_RECTS = False