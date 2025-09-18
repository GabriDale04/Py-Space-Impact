from core import Context
from game import *

game_ui_context = Context()

lives_text = LivesText(game_ui_context, LIVES_TEXT_FONT_SIZE)
weapon_text = WeaponText(game_ui_context, WEAPON_TEXT_FONT_SIZE)
score_text = ScoreText(game_ui_context, SCORE_TEXT_FONT_SIZE)
text_test = ThemeText(game_ui_context, FONT_SPACE_IMPACT_MENUS, 3)

game_context = Context()
game_over_context = Context()

game_over_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_text.set_text("Game Over")
game_over_score_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_score_text.set_text("Your score: ")
game_over_score_text.set_pos(0, game_over_text.y + game_over_text.height)
game_over_score_value_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_score_value_text.set_text("ABC123:-gtyyx")
game_over_score_value_text.set_pos(0, game_over_score_text.y + game_over_score_text.height)

player = Player(game_context)