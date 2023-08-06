from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
# flake8: noqa: F401
# expose main type and main func in package
from ohlc.types import Ohlc
from ohlc.candles.app import main

