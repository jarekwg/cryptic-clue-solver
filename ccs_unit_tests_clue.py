__author__ = 'Jarek Glowacki'

import unittest

from clue import Clue
from exceptions import *

class UnitTestsClue(unittest.TestCase):
	"""
	These tests check whether the input clues are correctly parsed.
	Additional Clue-specific testing is performed in the integration tests
	"""

	def test_validClueMinimal(self):
		c = Clue('This is a clue.')
		self.assertEqual(c.clue, 'This is a clue.')
		self.assertEqual(c.length, None)
		self.assertEqual(c.typ, None)
		self.assertEqual(c.known_letters, None)
		self.assertEqual(c.tokens, ['this', 'is', 'a', 'clue'])

	def test_validClueWithLength(self):
		c = Clue('This is a clue. (7)')
		self.assertEqual(c.clue, 'This is a clue.')
		self.assertEqual(c.length, 7)
		self.assertEqual(c.typ, None)
		self.assertEqual(c.known_letters, None)
		self.assertEqual(c.tokens, ['this', 'is', 'a', 'clue'])

	def test_validClueWithLengthAndType(self):
		c = Clue('This is a clue. (7)', typ='initial')
		self.assertEqual(c.clue, 'This is a clue.')
		self.assertEqual(c.length, 7)
		self.assertEqual(c.typ, 'initial')
		self.assertEqual(c.known_letters, None)
		self.assertEqual(c.tokens, ['this', 'is', 'a', 'clue'])

	def test_validClueWithLengthAndKnownLetters(self):
		c = Clue('This is a clue. (7)', known_letters='????p??')
		self.assertEqual(c.clue, 'This is a clue.')
		self.assertEqual(c.length, 7)
		self.assertEqual(c.typ, None)
		self.assertEqual(c.known_letters, '????p??')
		self.assertEqual(c.tokens, ['this', 'is', 'a', 'clue'])

	def test_validClueWithEverything(self):
		c = Clue('This is a clue. (7)', length=7, typ='anagram', known_letters='D???p??')
		self.assertEqual(c.clue, 'This is a clue.')
		self.assertEqual(c.length, 7)
		self.assertEqual(c.typ, 'anagram')
		self.assertEqual(c.known_letters, 'd???p??')
		self.assertEqual(c.tokens, ['this', 'is', 'a', 'clue'])

	def test_invalidClueLengthMismatch(self):
		self.assertRaises(SolutionLengthMismatchException, Clue, 'Random clue. (4)', 5)
		self.assertRaises(SolutionLengthMismatchException, Clue, 'Random clue. (4)', known_letters='?f?e???')


	def test_invalidClueMultiWordLength(self):
		self.assertRaises(UnsupportedClueException, Clue, 'Random clue. (4-4)')
		self.assertRaises(UnsupportedClueException, Clue, 'Random clue. (3,5)')