import sys
from . import roll

print(", ".join([str(roll(arg).value) for arg in sys.argv[1:]]))