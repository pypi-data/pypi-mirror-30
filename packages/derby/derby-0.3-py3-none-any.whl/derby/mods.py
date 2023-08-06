from heapq import nlargest, nsmallest 

class Mod:
    def __call__(self, dice, bonus):
        return dice, bonus

class AddMod(Mod):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, dice, bonus):
        return dice, bonus + self.value

class SubMod(Mod):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, dice, bonus):
        return dice, bonus - self.value

class MinMod(Mod):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, dice, bonus):
        return nsmallest(self.value, dice), bonus

class MaxMod(Mod):
    def __init__(self, value):
        self.value = value
    
    def __call__(self, dice, bonus):
        return nlargest(self.value, dice), bonus