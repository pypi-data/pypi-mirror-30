from forbiddenfruit import curse as monkey_patch
from omakase.functions import *


monkey_patch(list, 'len', lambda sequence: len(sequence))
monkey_patch(list, 'map', lambda sequence, function: map(function, sequence))
monkey_patch(list, 'filter', lambda sequence, function: filter(function, sequence))
monkey_patch(list, 'max', lambda sequence: max(sequence) if sequence else None)
monkey_patch(list, 'min', lambda sequence: min(sequence) if sequence else None)
monkey_patch(list, 'sum', lambda sequence: sum(sequence))
monkey_patch(list, 'zip', lambda sequence, other: zip(sequence, other))


monkey_patch(list, 'join', join)
monkey_patch(list, 'sortby', sortby)
monkey_patch(list, 'compact', compact)
monkey_patch(list, 'freq', freq)
monkey_patch(list, 'groupby', groupby)
monkey_patch(list, 'indexby', indexby)
monkey_patch(list, 'uniq', uniq)
monkey_patch(list, 'take', take)
monkey_patch(list, 'drop', drop)
monkey_patch(list, 'first', first)
monkey_patch(list, 'last', last)
monkey_patch(list, 'reduce', my_reduce)
