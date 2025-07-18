import math as Math
from PIL import Image

class math:
    @staticmethod
    def clamp(value : int, min_value : int, max_value : int):
        return max(min(value, max_value), min_value)
    
    @staticmethod
    def wrap(value : int, min_value : int, max_value : int):
        range_size = min_value - max_value + 1
        return ((value - min_value) % range_size) + max_value

class TextureAtlasGenerator:
    @staticmethod
    def generate(image_map : dict[str, str], img_size : int):
        num_images = len(image_map)
        grid_size = Math.ceil(Math.sqrt(num_images))
        atlas_dimension = grid_size * img_size

        print(atlas_dimension)