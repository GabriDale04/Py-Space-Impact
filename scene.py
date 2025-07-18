from core import GameObject
from game import Player

game_container = GameObject()

player = Player()

game_container.append_children([player])