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
            resource : str,
            width : int,
            height : int
        ):

        self.surface = pygame.image.load(resource)
        self.surface = pygame.transform.scale(self.surface, (width, height))

class GameObject:
    from config import DEBUG_SHOW_RECTS as __show_rects__

    def __init__(
            self,
            x : int = 0,
            y : int = 0,
            width : int = 0,
            height : int = 0,
            tag : str = None,
            animations: list[Sprite] = [],
            rect_color : tuple[int, int, int] = (0, 0, 0)
        ):

        self.rect = pygame.Rect(x, y, width, height)
        self.rect_color = rect_color
        
        self.tag = tag

        self.destroyed = False

        self.animations = animations
        self.current_animation = 0

        self.children : list[GameObject] = []
    
    def update(self):
        if self.destroyed:
            return

        if GameObject.__show_rects__ or len(self.animations) == 0:
            pygame.draw.rect(Window.screen, self.rect_color, self.rect)
        if len(self.animations) > 0:
            Window.screen.blit(self.animations[self.current_animation].surface, self.rect)

        new_children = []

        for child in self.children:
            if not child.destroyed:
                child.update()
                new_children.append(child)

        self.children = new_children
    
    def animate(self):
        self.current_animation = (self.current_animation + 1) % len(self.animations)

    def destroy(self):
        self.destroyed = True

    def append_child(self, child : 'GameObject'):
        self.children.append(child)

    def append_children(self, children : list['GameObject']):
        self.children.extend(children)
    
    def find_with_tag(self, tag : str) -> list['GameObject']:
        found : list['GameObject'] = []

        for child in self.children:
            if child.tag == tag:
                found.append(child)

            if len(child.children) > 0:
                found.extend(child.find_with_tag(tag))
        
        return found

    def collide(self, other : pygame.Rect) -> bool:
        if self.destroyed:
            return False

        return self.rect.colliderect(other)