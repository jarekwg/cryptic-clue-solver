# -*- coding: utf-8 -*-

"""
Similar to the clue class, this one creates wrappers around solution objects.
These wrappers contain the solution itself, the cloue, and information about how the solutions was reached.
It's primary function is to neatly store this information, and format it for printing when required.
"""

# Other CCS modules
import log  # module for giving runtime feedback to the user

__author__ = 'Jarek Glowacki'
logger = log.getLogger(__name__)

class Solution(object):
	def __init__(self, clue, solution, defpos, wordplay, certainty):
		self.clue = clue
		self.defpos = defpos
		if defpos is not None:
			self.definition = ' '.join(self.clue.tokens[
					0 if self.defpos > 0 else self.defpos:self.defpos if self.defpos > 0 else None]).upper()
			if wordplay[1] == 'brute-forced':
				self.wordplay = '---'
			else:
				self.wordplay = ' '.join(self.clue.tokens[
						0 if self.defpos < 0 else self.defpos:self.defpos if self.defpos < 0 else None]).upper()
		else:
			self.definition = '---'
			self.wordplay = '---'
		self.solution = solution
		self.keywordpos = wordplay[0]
		self.typ = wordplay[1]
		self.applied_to = wordplay[2]
		self.certainty = certainty

	def __str__(self):
		return 'Definition part: ' + self.definition + \
				 '\nWordplay part: ' + self.wordplay + \
				 '\nKeyword: ' + (self.clue.tokens[self.keywordpos].upper() if self.keywordpos >= 0 else '---') + \
				 ' <' + self.typ + '> applied to: ' + self.applied_to.upper() + \
				 '\nSolution: ' + self.solution.upper().replace('_',' ') + \
				 '\nCertainty: ' + str(self.certainty) + '\n'

	def __repr__(self):
		return '='*15 + '\n' + str(self) + '='*15 + '\n'


class WordplaySolution(object):
	"""
	A simplified version of the solution object, for storing intermediate wordplay solutions.
	"""

	def __init__(self, solution, typ, applied_to, certainty):
		self.solution = solution
		self.typ = typ
		self.applied_to = applied_to
		self.certainty = certainty

	def __repr__(self):
		return self.solution.upper().replace('_',' ') + ' <' + self.typ + '> (@ ' + ' '.join(self.applied_to).upper() + \
				 ', score: ' + str(self.certainty) + ')'