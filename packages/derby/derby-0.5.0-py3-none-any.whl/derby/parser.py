from lark import Lark 
from .grammar import grammar
from .transformer import DiceTransformer

parser = Lark(grammar, parser='lalr', transformer=DiceTransformer())