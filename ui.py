from core import Context, GameObject
from config import *

class TextChar(GameObject):
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            font_family : str,
            value : str
        ):

        texture_atlas : TextureAtlas = None
        char_map : dict[str, tuple[int, int]] = None
        width = 0
        height = 0

        if font_family == FONT_FAMILY_NUMBERS:
            texture_atlas = FONT_NUMBERS_TEXTURE_ATLAS
            char_map = FONT_NUMBERS_CHAR_MAP
            width = FONT_NUMBERS_CHAR_WIDTH
            height = FONT_NUMBERS_CHAR_HEIGHT

        coords = char_map.get(value)
        sprite = Sprite.from_surface(texture_atlas.get_sprite(coords[0], coords[1]), width, height)

        super().__init__(
            context = context,
            x = x,
            y = y,
            width = width,
            height = height,
            animations = [sprite],
            rect_color = FONT_RECT_COLOR
        )

class Text:
    def __init__(
            self,
            context : Context,
            x : int,
            y : int,
            font_family : str,
            value : str  
        ):

        self.context = context

        if font_family == FONT_FAMILY_NUMBERS:
            # The gap between each character
            self.gap = FONT_NUMBERS_CHAR_GAP
            # The width of a single character and so the entire text
            self.height = FONT_NUMBERS_CHAR_HEIGHT

            # The width of a single character
            self.char_width = FONT_NUMBERS_CHAR_WIDTH

        self.characters : list[TextChar] = []
        # The total width of the text
        self.width = -self.gap

        for c in value:
            char = TextChar(context, x, y, font_family, c)
            self.characters.append(char)

            x += self.char_width + self.gap
            self.width += self.char_width + self.gap
    
    def destroy(self):
        for c in self.characters:
            c.destroy()

    def set_pos(self, x : int, y : int):
        for c in self.characters:
            c.rect.x = x
            c.rect.y = y

            x += self.char_width + self.gap