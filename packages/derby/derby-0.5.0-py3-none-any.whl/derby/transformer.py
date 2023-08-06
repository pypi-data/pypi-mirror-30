from random import randint
from lark import Transformer, inline_args
from .derby import Roll
from .mods import AddMod, SubMod, MinMod, MaxMod

mods = {
    'add': AddMod,
    'sub': SubMod,
    'low': MinMod,
    'high': MaxMod
}



class DiceTransformer(Transformer):
    @inline_args
    def dice_expand(self, times, size, *mods):
        return Roll([randint(1, size) for _ in range(times)], *mods)

    @inline_args
    def mod_expand(self, mod, value):
        return mods[mod.data](value)

    number = inline_args(int)
    roll = dice_expand
    mod = mod_expand