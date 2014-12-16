# -*- coding: utf-8 -*-

import unittest
import pdb

from clue_parser import ClueParser
from clue import Clue

class IntegrationTests(unittest.TestCase):
	"""
	These tests run a list of simple cryptic clues through the system, expecting it to be capable of solving them.
	Each test provides the clue in a slightly different format, ensuring that each of these formats is supported.
	"""


	@classmethod
	def setUpClass(cls):
		cls.cp = ClueParser()

	###
	# Tests determining whether the solver solves some basic cryptic clues as expected.
	# Input clue + hints are in raw form (ie. not provided as Clue object).
	###

	def test_clueParsingRawTextClueOnly(self):
		s = self.cp.parseClue('Book in Habib Lew\'s handbag.')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('bible', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('run', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingRawTextSolnLengthInText(self):
		s = self.cp.parseClue('Punch a Rio Tinto official; find transport. (7)')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('chariot', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('run', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingRawTextSolnLengthSeparate(self):
		s = self.cp.parseClue('A pint makes colour.', 5)
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('paint', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('anagram', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingRawTextWordplayTypeGiven(self):
		s = self.cp.parseClue('Frida, ILY - said Tom, holding a newspaper.', typ='run')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('daily', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('run', s.typ, 'Wrong wordplay type applied!')

	###
	# Tests determining whether the solver solves some basic cryptic clues as expected.
	# Input clue + hints are provided as Clue object.
	###

	def test_clueParsingClueObjectClueOnly(self):
		s = self.cp.parseClue(Clue('Guide graphite'))
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('lead', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('double definition', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingClueObjectSolnLengthInText(self):
		s = self.cp.parseClue(Clue('House of God in Sencha Pellegrini bar. (6)'))
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('chapel', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('run', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingClueObjectSolnLengthSeparate(self):
		s = self.cp.parseClue(Clue('In job, sole technician, dated.', 8))
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('obsolete', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('run', s.typ, 'Wrong wordplay type applied!')

	def test_clueParsingClueObjectWordplayTypeGiven(self):
		s = self.cp.parseClue(Clue('Zoroastrian pairs dancing.', typ='anagram'))
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('parsi', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('anagram', s.typ, 'Wrong wordplay type applied!')

	###
	# Other random tests.
	###

	def test_clue(self):
		s = self.cp.parseClue('Exuviate garage.')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('shed', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('double definition', s.typ, 'Wrong wordplay type applied!')

	def test_clueCharade1(self):
		s = self.cp.parseClue('First man at carpet.', 3)
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('mat', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('charade', s.typ, 'Wrong wordplay type applied!')

	def test_clueCharade2(self):
		s = self.cp.parseClue('Initially babies are naked.', 4)
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('bare', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('charade', s.typ, 'Wrong wordplay type applied!')

	def test_clueCharade3(self):
		s = self.cp.parseClue('Prosciutto teases beds.', 8)
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('hammocks', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('charade', s.typ, 'Wrong wordplay type applied!')

	def test_clueCharade4(self):
		s = self.cp.parseClue('Rip lunch, last supper!', 4)
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('tear', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('charade', s.typ, 'Wrong wordplay type applied!')

	def test_clueCharade5(self):
		s = self.cp.parseClue('First male orphan on Io. (4)')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('moon', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('charade', s.typ, 'Wrong wordplay type applied!')

	def test_clueInitial1(self):
		s = self.cp.parseClue('Purchased Game of Thrones, initially. (3)')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('got', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('initial', s.typ, 'Wrong wordplay type applied!')

	def test_clueFinal(self):
		s = self.cp.parseClue('Finally purchased Game Arena of hard of hearing. (4)', known_letters='???F')
		self.assertGreater(len(s), 0, 'Should find at least one solution!')
		s = s[0]
		self.assertEqual('deaf', s.solution, 'Wrong solution found at first position!')
		self.assertEqual('final', s.typ, 'Wrong wordplay type applied!')

# If this script is executed directly, it will run its test!
if __name__ == "__main__":
	# Supposedly the unittest library has a bug where it throws resource warnings
	# when it shouldn't. Hence, opting to hide these.
	unittest.main(warnings='ignore')