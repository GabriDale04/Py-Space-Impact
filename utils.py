from config import USE_16BIT_INTEGERS, FREEZE_SCORE_ON_OVERFLOW

class math:
    INT16_MIN_VALUE = -0x8000
    INT16_MAX_VALUE = 0x7FFF
    INT32_MIN_VALUE = -0x80000000
    INT32_MAX_VALUE = 0x7FFFFFFF

    @staticmethod
    def clamp(value : int, min_value : int, max_value : int):
        return max(min(value, max_value), min_value)
    
    @staticmethod
    def wrap(value: int, min_value: int, max_value: int):
        range_size = max_value - min_value + 1
        return ((value - min_value) % range_size) + min_value

INT_MIN_VALUE = math.INT16_MIN_VALUE if USE_16BIT_INTEGERS else math.INT32_MIN_VALUE
INT_MAX_VALUE = math.INT16_MAX_VALUE if USE_16BIT_INTEGERS else math.INT32_MAX_VALUE

def int_b(value : int):
    if FREEZE_SCORE_ON_OVERFLOW and value > INT_MAX_VALUE:
        return INT_MAX_VALUE
    if value < INT_MIN_VALUE or value > INT_MAX_VALUE:
        return math.wrap(value, INT_MIN_VALUE, INT_MAX_VALUE)

    return value