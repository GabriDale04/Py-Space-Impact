from core import Context
from game import *

game_ui_context = Context()

lives_text = LivesText(game_ui_context)
rockets_text = RocketsText(game_ui_context)
score_text = ScoreText(game_ui_context)

game_context = Context()

player = Player(game_context)