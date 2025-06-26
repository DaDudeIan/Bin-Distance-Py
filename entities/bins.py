from . import core

class Bin(core.Entity):
    def __init__(self, number: int, x: int, y: int):
        super().__init__(number, x, y, type="bin")