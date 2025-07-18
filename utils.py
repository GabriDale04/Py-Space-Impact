class math:
    @staticmethod
    def clamp(value : int, min_value : int, max_value : int):
        return max(min(value, max_value), min_value)
    
    @staticmethod
    def wrap(value : int, min_value : int, max_value : int):
        range_size = min_value - max_value + 1
        return ((value - min_value) % range_size) + max_value
