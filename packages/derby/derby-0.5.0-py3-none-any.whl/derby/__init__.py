from .derby import Roll
from .mods import AddMod, SubMod, MaxMod, MinMod
from .parser import parser

def roll(query):
    return parser.parse(query)