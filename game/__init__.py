"""
Chess Game Package
-----------------
A chess game implementation with AI opponents.
"""

from .game import Game
from .BasicAI import BasicAI
from .ProAI import ProAI

__version__ = '1.0.0'
__author__ = 'nhanvatphu04'

__all__ = [
    'Game',
    'BasicAI', 
    'ProAI'
]
