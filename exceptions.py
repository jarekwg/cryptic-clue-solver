# -*- coding: utf-8 -*-

"""
A list of custom exceptions that CCS can generated. The GUI already handles them where necessary.
"""

__author__ = 'Jarek Glowacki'

class UnsupportedClueException(Exception):
	pass

class SolutionLengthMismatchException(Exception):
	pass

class BruteForceWithoutKnownLettersException(Exception):
	pass