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
    
    def get_sprite(self, x : int, y : int) -> Sprite:
        x = x * self.textures_width + x * self.textures_gap
        y = y * self.textures_height + y * self.textures_gap
        rect = pygame.Rect(x, y, self.textures_width, self.textures_height)
        subsurface = self.surface.subsurface(rect)

        return subsurface

class Context:
    def __init__(self):
        self.game_objects : list[GameObject] = []
    
    def update(self):
        new_list = []

        for obj in self.game_objects:
            if not obj.destroyed:
                obj.update()
                new_list.append(obj)

        self.game_objects = new_list

    def append(self, game_object : 'GameObject'):
        self.game_objects.append(game_object)

    def find_with_tag(self, tag : str) -> list['GameObject']:
        found : list[GameObject] = []

        for obj in self.game_objects:
            if obj.tag == tag:
                found.append(obj)
        
        return found  

class GameObject:
    from config import DEBUG_SHOW_RECTS as __show_rects__

    def __init__(
            self,
            context : Context,
            x : int = 0,
            y : int = 0,
            width : int = 0,
            height : int = 0,
            tag : str = None,
            animations: list[Sprite] = [],
            rect_color : tuple[int, int, int] = (0, 0, 0)
        ):

        self.context = context
        context.append(self)

        self.rect = pygame.Rect(x, y, width, height)
        self.rect_color = rect_color
        
        self.tag = tag

        self.destroyed = False

        self.animations = animations
        self.current_animation = 0
    
    def update(self):
        if self.destroyed:
            return

        if GameObject.__show_rects__ or len(self.animations) == 0:
            pygame.draw.rect(Window.screen, self.rect_color, self.rect)
        if len(self.animations) > 0:
            Window.screen.blit(self.animations[self.current_animation].surface, self.rect)
    
    def animate(self):
        self.current_animation = (self.current_animation + 1) % len(self.animations)

    def destroy(self):
        self.destroyed = True

    def collide(self, other : pygame.Rect) -> bool:
        if self.destroyed:
            return False

        return self.rect.colliderect(other)