from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from builtins import next
from builtins import range
from future import standard_library
standard_library.install_aliases()
from random import random as _rand
from ohlc.types import ZERO, Ohlc

def random_values_generator( **_3to2kwargs):
    if 'v_max' in _3to2kwargs: v_max = _3to2kwargs['v_max']; del _3to2kwargs['v_max']
    else: v_max = None
    if 'v_min' in _3to2kwargs: v_min = _3to2kwargs['v_min']; del _3to2kwargs['v_min']
    else: v_min = None
    if 'amp' in _3to2kwargs: amp = _3to2kwargs['amp']; del _3to2kwargs['amp']
    else: amp = 0.2
    if 'count' in _3to2kwargs: count = _3to2kwargs['count']; del _3to2kwargs['count']
    else: count = float('inf')
    if 'v_start' in _3to2kwargs: v_start = _3to2kwargs['v_start']; del _3to2kwargs['v_start']
    else: v_start = 0.1
    if 0.0 in [v_start, v_min, v_max]:
        raise ValueError('start, min, and max values cannot be zero')
    v_start = float(v_start)
    if v_min is None: v_min = v_start / 10
    if v_max is None: v_max = v_start * 10
    v_min, v_max = float(v_min), float(v_max)
    if not v_min <= v_start <= v_max:
        raise ValueError('start not between min and max values')
    i = 0
    v = v_start
    while i < count:
        i += 1
        v = max(v_min, min(v_max, v + amp * v * (_rand() - _rand())))
        if v == 0.0: v = max(v_min, min(v_max, ZERO))
        yield v

def random_ohlc_generator( **_3to2kwargs):
    if 'v_min' in _3to2kwargs: v_min = _3to2kwargs['v_min']; del _3to2kwargs['v_min']
    else: v_min = None
    if 'v_max' in _3to2kwargs: v_max = _3to2kwargs['v_max']; del _3to2kwargs['v_max']
    else: v_max = None
    if 'step' in _3to2kwargs: step = _3to2kwargs['step']; del _3to2kwargs['step']
    else: step = 10
    if 'count' in _3to2kwargs: count = _3to2kwargs['count']; del _3to2kwargs['count']
    else: count = float('inf')
    if 'v_start' in _3to2kwargs: v_start = _3to2kwargs['v_start']; del _3to2kwargs['v_start']
    else: v_start = 0.1
    nums = random_values_generator(v_start=v_start, v_max=v_max, v_min=v_min)
    values = [float(v_start)]
    i = 0
    o = None
    while i < count:
        # keep last values from prev. batch to allow open-close transition
        values = [values[-1]] + [next(nums) for _ in range(step)]
        i += 1
        o = Ohlc.from_values(values, prev=o)
        yield o

