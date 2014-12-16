# -*- coding: utf-8 -*-

"""
This class creates wrappers around clues submitted by the user. These wrappers contain the clue itself, along with
 (if supplied) the wordlength, known letters and wordplay type.
It performs a degree of validation on incoming clues, and is also capable of checking whether proposed solutions
 conform to these clue specifications.
"""

# Python libraries
import re  # regex library
import pdb

# Dictionary libraries
from nltk.tokenize import RegexpTokenizer

# Other CCS modules
from exceptions import *  # custom CCS exceptions
import log  # module for giving runtime feedback to the user

__author__ = "Jarek Glowacki"
logger = log.getLogger(__name__)
tokenizer = RegexpTokenizer(r'\w+')


class Clue(object):
	def __init__(self, clue, length=None, typ=None, known_letters=None):
		# Attempt to extract length from end of clue.
		match = re.search('(.*?)\s*\(([\d,-]+)\)\s*', clue)
		if match:
			clue = match.group(1)
			try:
				length_matched = int(match.group(2))
			except ValueError:
				raise UnsupportedClueException('Invalid word length: \'%s\'. Only single word answers supported!' % match.group(2))
			if length is None:
				length = length_matched
			elif length_matched != length:
				raise SolutionLengthMismatchException
		if known_letters:
			known_letters = known_letters.lower()
			self.regex = '\A' + known_letters.replace('?','[a-z]') + '\Z' # for efficiency later
			if length is None:
				length = len(known_letters)
			elif len(known_letters) != length:
				raise SolutionLengthMismatchException
		if length is None:
			logger.debug('No word length provided with clue: %s' % clue)

		# Record the processed parameters.
		self.clue = clue
		self.length = length
		self.typ = typ
		self.known_letters = known_letters

		# Tokenise.
		self.tokens = tokenizer.tokenize(self.clue.replace("'", '').lower())
		self.token_set = set(self.tokens) # for efficiency later

	def checkSolution(self, soln):
		"""
		Returns true iff the given soln satisfies the constraints presented by the clue.
		This includes filtering by:
			-clue length
			-whether the supposed soln is a word already in the clue
			-known letters
		Note that filtering by type is not necessary as disallowed wordplay types will not be generating
		 any wordplay solutions in the
		  first place.
		"""

		soln = soln.replace('_', '')
		# Filter out if solution is just a token from the original clue.
		if soln in self.token_set:
			return False
		# Filter by known letters
		if self.known_letters:
			#pdb.set_trace()
			if not re.search(self.regex, soln):
				return False
		# Filter by length.
		elif (self.length and len(soln) != self.length) or len(soln) < 3:
			return False
		return True

	def __repr__(self):
		return '%s (%s) <typ=%s, letters=%s>' % (self.clue, self.length, self.typ, self.known_letters)
