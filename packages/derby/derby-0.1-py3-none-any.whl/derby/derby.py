class Dice:
    def __init__(self, dice, *mods):
        self.dice = dice 
        self.mods = mods 
    
    def result(self):
        dice, value = self.dice, 0
        for mod in self.mods:
            dice, value = mod(dice, value)
        return dice, value + sum(dice)