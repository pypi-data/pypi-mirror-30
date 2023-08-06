from functools import reduce

class Roll:
    def __init__(self, dice, *mods):
        self.dice = dice 
        self.mods = mods
    
    @property
    def value(self):
        return self.result()[1]
    
    def result(self):
        dice, value = self.dice, 0
        for mod in self.mods:
            dice, value = mod(dice, value)
        return dice, value + sum(dice)
    
    def json(self):
        dice, value = self.result()
        return {
            'dice': dice,
            'result': value 
        }
