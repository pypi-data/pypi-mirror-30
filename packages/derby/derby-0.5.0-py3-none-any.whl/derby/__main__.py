import sys
from . import roll

try:
    print(", ".join([str(roll(arg).value) for arg in sys.argv[1:]]))
except:
    print('bad input: {}'.format("".join(sys.argv[1:])))