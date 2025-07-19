from config import USE_16BIT_INTEGERS

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

class int_b:
    MIN_VALUE = math.INT16_MIN_VALUE if USE_16BIT_INTEGERS else math.INT32_MIN_VALUE
    MAX_VALUE = math.INT16_MAX_VALUE if USE_16BIT_INTEGERS else math.INT32_MAX_VALUE

    def __init__(self, value : int):
        self.value = int(value)

        if value < int_b.MIN_VALUE or value > int_b.MAX_VALUE:
            self.value = math.wrap(value, int_b.MIN_VALUE, int_b.MAX_VALUE)

    def __add__(self, other):
        return int_b(self.value + int(other))

    def __sub__(self, other):
        return int_b(self.value - int(other))

    def __mul__(self, other):
        return int_b(self.value * int(other))
    
    def __truediv__(self, other):
        return int_b(self.value / int(other))
    
    def __mod__(self, other):
        return int_b(self.value % int(other))

    def __floordiv__(self, other):
        return int_b(self.value // int(other))

    def __eq__(self, other):
        return self.value == int(other)

    def __ne__(self, other):
        return self.value != int(other)
    
    def __lt__(self, other):
        return self.value < int(other)
    
    def __le__(self, other):
        return self.value <= int(other)

    def __gt__(self, other):
        return self.value > int(other)

    def __ge__(self, other):
        return self.value >= int(other)

    def __str__(self):
        return str(self.value)