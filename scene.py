from core import Context
from game import *

game_ui_context = Context()

lives_text = LivesText(game_ui_context, LIVES_TEXT_FONT_SIZE)
weapon_text = WeaponText(game_ui_context, WEAPON_TEXT_FONT_SIZE)
score_text = ScoreText(game_ui_context, SCORE_TEXT_FONT_SIZE)

game_context = Context()

player = Player(game_context)