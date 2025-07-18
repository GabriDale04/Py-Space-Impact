from core import Context
from game import *
from ui import *

game_ui_context = Context()

text = Text(game_ui_context, 0, 0, FONT_FAMILY_NUMBERS, "11111")
text.set_pos((WINDOW_WIDTH // 3) * 2 + text.width // 3, 0)

game_context = Context()

player = Player(game_context)
comet = Comet(game_context, MAP_RIGHT_BOUND, 200, 5, 1, DOWN)
shuttle = Shuttle(game_context, MAP_RIGHT_BOUND, 400, 3, 2, DOWN)
rocket = Rocket(game_context, MAP_RIGHT_BOUND, 400, 1, 1, DOWN)