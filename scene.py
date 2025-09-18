from core import Context
from game import *

game_ui_context = Context()

lives_text = LivesText(game_ui_context, LIVES_TEXT_FONT_SIZE)
weapon_text = WeaponText(game_ui_context, WEAPON_TEXT_FONT_SIZE)
score_text = ScoreText(game_ui_context, SCORE_TEXT_FONT_SIZE)

game_context = Context()
game_over_context = Context()

game_over_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_text.set_text("Game Over")
game_over_score_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_score_text.set_text("Your score: ")
game_over_score_text.set_pos(0, FONT_SPACE_IMPACT_MENUS_TEXTURE_ATLAS_CHAR_HEIGHT * game_over_text.font_size)
game_over_score_value_text = ThemeText(game_over_context, FONT_SPACE_IMPACT_MENUS, 10)
game_over_score_value_text.set_text("ABC123:-gtyyx")
game_over_score_value_text.set_pos(0, 2 * FONT_SPACE_IMPACT_MENUS_TEXTURE_ATLAS_CHAR_HEIGHT * game_over_text.font_size)

player = Player(game_context)