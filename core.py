import pygame

class Window:
    screen : pygame.Surface = None

    @staticmethod
    def init():
        from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE

        Window.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

class Sprite:
    def __init__(
            self,
            surface : pygame.Surface
        ):
            self.surface = surface
    
    @staticmethod
    def load(resource : str, width : int, height : int):
        surface = pygame.image.load(resource)
        surface = pygame.transform.scale(surface, (width, height))
        return Sprite(surface)

    @staticmethod
    def from_surface(surface : pygame.Surface, width : int, height : int) -> 'Sprite':
        surface = pygame.transform.scale(surface, (width, height))
        return Sprite(surface)

class TextureAtlas:
    def __init__(
        self,
        resource : str,
        textures_width : int,
        textures_height : int,
        textures_gap : int
    ):
        self.surface = pygame.image.load(resource)

        self.textures_width = textures_width
        self.textures_height = textures_height
        self.textures_gap = textures_gap
    
    def get_sprite(self, x : int, y : int, width : int = -1, height : int = -1) -> Sprite:
        width = self.textures_width if width == -1 else width
        height = self.textures_height if height == -1 else height

        x = x * self.textures_width + x * self.textures_gap
        y = y * self.textures_height + y * self.textures_gap
        rect = pygame.Rect(x, y, width, height)
        subsurface = self.surface.subsurface(rect)

        return Sprite(subsurface)

class Context:
    def __init__(self):
        self.game_objects : list[GameObject] = []

    def update(self):
        new_list = []

        for obj in self.game_objects:
            if not obj.destroyed:
                obj.on_render()
                obj.update()
                new_list.append(obj)

        self.game_objects = new_list

    def append(self, game_object : 'GameObject'):
        self.game_objects.append(game_object)

    def find_with_tag(self, tag : str) -> list['GameObject']:
        found : list['GameObject'] = []

        for obj in self.game_objects:
            if obj.tag == tag:
                found.append(obj)
        
        return found
    
    def find_with_tags(self, tags : list[str]) -> list['GameObject']:
        found : list[GameObject] = []

        for obj in self.game_objects:
            if obj.tag in tags:
                found.append(obj)
        
        return found

class GameObject:
    def __init__(
            self,
            context : Context,
            x : int = 0,
            y : int = 0,
            width : int = 0,
            height : int = 0,
            tag : str = None,
            sprite: Sprite = None,
            rect_color : tuple[int, int, int] = (0, 0, 0)
        ):

        from config import DEBUG_SHOW_RECTS as __show_rects__
        self.__show_rects__ = __show_rects__

        self.context = context
        context.append(self)

        self.rect = pygame.Rect(x, y, width, height)
        self.rect_color = rect_color
        
        self.tag = tag

        self.destroyed = False

        self.sprite = sprite

    def on_render(self):
        if self.__show_rects__:
            pygame.draw.rect(Window.screen, self.rect_color, self.rect)
        if self.sprite != None:
            Window.screen.blit(self.sprite.surface, self.rect)

    def update(self):
        pass

    def destroy(self):
        self.destroyed = True

    def collide(self, other : 'GameObject') -> bool:
        if self.destroyed or other.destroyed:
            return False

        return self.rect.colliderect(other.rect)

class Font:
    def __init__(
            self,
            font_source : TextureAtlas,
            font_map : dict,
            char_width : int,
            char_height : int,
            char_gap : int
        ):
    
        self.font_source = font_source
        self.font_map = font_map
        self.char_width = char_width
        self.char_height = char_height
        self.char_gap = char_gap
    
    def get_sprite(self, char : str, font_size : int) -> Sprite:
        item = self.font_map[char]
        coords = item["coords"]
        size = item["size"]

        return Sprite.from_surface(self.font_source.get_sprite(coords[0], coords[1], size[0], size[1]).surface, size[0] * font_size, size[1] * font_size)

class Text:
    def __init__(
            self,
            context : Context,
            font : Font,
            font_size : int
        ):

        from config import FONT_RECT_COLOR as __font_rect_color__
        self.__font_rect_color__ = __font_rect_color__

        self.context = context
        self.font = font
        self.font_size = font_size
        self.font_gap = font.char_gap * font_size
        self.x = 0
        self.y = 0
        self.characters : list[GameObject] = []
    
    def clear(self):
        for char in self.characters:
            char.destroy()

        self.characters = []
        self.width = 0

    def set_text(self, value : str):
        self.clear()
        x = self.x
        self.width = 0 if len(value) == 0 else -self.font_gap

        for char in value:
            sprite = self.font.get_sprite(char, self.font_size)
            rect_width = self.font.font_map[char]["size"][0] * self.font_size
            rect_height = self.font.font_map[char]["size"][1] * self.font_size

            text_char = GameObject(
                context = self.context,
                x = x,
                y = self.y,
                width = rect_width,
                height = rect_height,
                sprite = sprite,
                rect_color = self.__font_rect_color__
            )

            self.characters.append(text_char)

            increment = rect_width + self.font_gap
            x += increment
            self.width += increment
    
    def set_pos(self, x : int, y : int):
        self.x = x
        self.y = y

        for char in self.characters:
            char.rect.x = x
            char.rect.y = y

            x += char.rect.width + self.font_gap
    
    @staticmethod
    def width_of(string : str, font : Font, font_size : int) -> int:
        width = 0 if len(string) == 0 else -font.char_gap * font_size

        for char in string:
            width += (font.font_map[char]["size"][0] + font.char_gap) * font_size
        
        return width

class Input:
    keys : list[int] = []
    keysdown : list[int] = []
    
    @staticmethod
    def getkeydown(key : int) -> bool:
        return key in Input.keysdown

    @staticmethod
    def getkey(key : int) -> bool:
        return Input.keys[key]