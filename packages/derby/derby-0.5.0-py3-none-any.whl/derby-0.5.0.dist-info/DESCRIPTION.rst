# derby
simple dice rolling library

```python

from derby import roll

stats = ['str','int','wis','dex','con','cha']
character = { stat: roll('3d6').value for stat in stats } # roll('4d6h3') if your GM is nice enough

```

## examples

```python
roll('1d20+1')
roll('2d20h1+1') # rolling with advantage
# or
roll('2d20+1h1') # mod order is pretty flexible
# but
roll('3d6 h2 l1') != roll('3d6 l1 h2')
```

# command line

```bash
$ python -m derby 2d10 1d20 3d6+1
```

