import random

from config import (
    USE_16BIT_INTEGERS, 
    FREEZE_SCORE_ON_OVERFLOW,
    MAP_LEFT_BOUND,
    MAP_RIGHT_BOUND,
    MAP_TOP_BOUND,
    MAP_BOTTOM_BOUND,
    UP,
    DOWN,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

def clamp(value : int, min_value : int, max_value : int) -> int:
    return max(min(value, max_value), min_value)

def wrap(value: int, min_value: int, max_value: int) -> int:
    range_size = max_value - min_value + 1
    return ((value - min_value) % range_size) + min_value

INT_MIN_VALUE = -0x8000 if USE_16BIT_INTEGERS else -0x80000000
INT_MAX_VALUE = 0x7FFF if USE_16BIT_INTEGERS else 0x7FFFFFFF

def int_b(value : int) -> int:
    if FREEZE_SCORE_ON_OVERFLOW and value > INT_MAX_VALUE:
        return INT_MAX_VALUE
    if value < INT_MIN_VALUE or value > INT_MAX_VALUE:
        return wrap(value, INT_MIN_VALUE, INT_MAX_VALUE)

    return value

def args(**kwArgs):
    return kwArgs

def random_y():
    return random.randint(MAP_TOP_BOUND, MAP_BOTTOM_BOUND)

def random_vertical_direction():
    return DOWN if random.randint(0, 1) == 0 else UP

def center_y(top_offset : int) -> int:
    return MAP_TOP_BOUND + (WINDOW_HEIGHT - MAP_TOP_BOUND - (WINDOW_HEIGHT - MAP_BOTTOM_BOUND)) // 2 + top_offset