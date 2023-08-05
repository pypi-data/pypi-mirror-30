from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from drawille import Turtle
from typing import List
from ohlc.types import Ohlc

def drawille_frame(data, **_3to2kwargs):
    if 'offset' in _3to2kwargs: offset = _3to2kwargs['offset']; del _3to2kwargs['offset']
    else: offset = 0.0
    if 'scale' in _3to2kwargs: scale = _3to2kwargs['scale']; del _3to2kwargs['scale']
    else: scale = 4.0
    t = Turtle()
    scaled = (o.transform(scale, offset) for o in data)
    x = 0
    for o,h,l,c in scaled:
        x += 1
        top = max(o,c)
        bot = min(o,c)
        t.up(); t.move(x, bot); t.down()
        # draw box
        t.move(x, top)
        t.move(x + 2, top)
        t.move(x + 2, bot)
        t.move(x, bot)
        # draw spikes
        t.up(); t.move(x + 1, l); t.down()
        if o <= c:
            t.move(x + 1, bot); t.up()    # draw lower bullish spike
            t.move(x + 1, top); t.down()  # move to upper bullish spike

        t.move(x + 1, h)  # draw uppper bullish or full bearish spike
        t.up()
        x += 3
    return t.frame()

