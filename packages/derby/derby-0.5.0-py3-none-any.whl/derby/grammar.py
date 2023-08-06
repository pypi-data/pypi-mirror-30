grammar = """
?start: roll
roll: number ("d"|"D") number [mod+]

mod: op number
op: "+" -> add
   | "-" -> sub
   | "l" -> low
   | "h" -> high

number: INT

%import common.INT
%import common.WS
%ignore WS
"""