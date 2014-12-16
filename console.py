"""
A basic environment script that prepares the most used modules for easy access.
It is executed automatically when a new PyCharm console is started.
"""

__author__ = 'Jarek'
import numpy as np

from clue_parser import ClueParser
from clue import Clue
import wordnet
import CCS

cp = ClueParser()