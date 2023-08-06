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

def dice_expand(t, times, size, *mods):
    return Roll([randint(1, size) for _ in range(times)], *mods)

def mod_expand(t, mod, value):
    return mods[mod.data](value)

class DiceTransformer(Transformer):
    number = inline_args(int)
    roll = inline_args(dice_expand)
    mod = inline_args(mod_expand)