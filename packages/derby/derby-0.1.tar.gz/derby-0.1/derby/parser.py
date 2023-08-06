from lark import Lark 

grammer = """
?start: roll

roll: dice+
dice: number ("d"|"D") number [mod+]

mod: (ams|sms)

?ams: op number
?sms: sel number

op: "+" -> add
  | "-" -> sub

sel: "l" -> low
   | "h" -> high

number: INT

%import common.INT
%import common.WS
%ignore WS
"""

parser = Lark(grammer)