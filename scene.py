from core import GameObject
from game import *

game_container = GameObject()

player = Player()
comet = Comet(500, 200)

game_container.append_children([player, comet])