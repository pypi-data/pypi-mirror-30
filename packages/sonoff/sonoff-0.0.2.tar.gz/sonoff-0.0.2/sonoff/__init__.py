"""
Python package for controlling Yeelight Sunflower bulbs.

Provides an API for creating a Hub by specified IP address, finding the bulbs
associated with it and sending commands to control those bulbs.

Hardware: https://www.yeelight.com/en_US/product/yeelight-sunflower
Project repo: https://github.com/lindsaymarkward/python-yeelight-sunflower
PyPI: https://pypi.python.org/pypi/yeelightsunflower
"""

from sonoff.main import Hub, Bulb

__title__ = 'sonoff'
__version__ = '0.0.2'
__author__ = 'Gerswin Pineda'
__license__ = 'MIT'
