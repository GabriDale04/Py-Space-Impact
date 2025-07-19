from core import Context
from game import *

game_ui_context = Context()

text = Text(game_ui_context, FONT_SPACE_IMPACT_COUNTERS, "0123456789>v")

game_context = Context()

player = Player(game_context)
comet = Comet(game_context, MAP_RIGHT_BOUND, 200, 5, 1, DOWN)
shuttle = Shuttle(game_context, MAP_RIGHT_BOUND, 400, 3, 2, DOWN)
rocket = Rocket(game_context, MAP_RIGHT_BOUND, 400, 1, 1, DOWN)