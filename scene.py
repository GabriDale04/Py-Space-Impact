from core import Context
from game import *

game_ui_context = Context()

lives_text = LivesText(game_ui_context)
rockets_text = RocketsText(game_ui_context)
score_text = ScoreText(game_ui_context)

game_context = Context()

player = Player(game_context)
comet = Comet(game_context, MAP_RIGHT_BOUND, 200, 5, 1, DOWN)
shuttle = Shuttle(game_context, MAP_RIGHT_BOUND, 400, 3, 2, DOWN)
rocket = Rocket(game_context, MAP_RIGHT_BOUND, 400, 1, 1, DOWN)