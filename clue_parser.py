# -*- coding: utf-8 -*-

"""
This is the top-level non-GUI module.
This is the module that should be imported if one wishes to avoid the GUI and dive straight
 into the source-code functionality.
A new ClueParser instance can be initialised as follows:
	cp = ClueParser()
After this, clues can be submitted for solving by typing (for example):
	cp.parseClue('Zoroastrian pairs dancing. (5)')

The parser employs certain heuristics to speed up computation:
	-Minimum solution length is 3 letters (not counting hyphens/apostrophes).
	-Solution is not the same as any of the clue tokens.
	-Solution is a single (possibly hyphenated) word.
	-Definitions are not longer than three words.
"""


# Python libraries
import inspect  # for parsing through the contents of python modules
import pdb  # live debugging module

# Dictionary libraries
import wordnet # custom wrapper around NLTK WordNet

# Other CCS modules
from clue import Clue
from solution import Solution
from exceptions import BruteForceWithoutKnownLettersException
import wordplay
import log  # module for giving runtime feedback to the user

__author__ = 'Jarek Glowacki'
logger = log.getLogger(__name__, streamLevel=log.INFO)

DEFINITION_MAX_LEN = 3

class ClueParser(object):
	def __init__(self, gui_thread=None):
		self.gui_thread = gui_thread

		# Create an instance of each existing wordplay type, based on what's
		#  been defined in the wordplay module.
		self.wordplays = {mem.__typ__: mem() for _, mem in inspect.getmembers(wordplay, inspect.isclass) \
								if issubclass(mem, wordplay.Wordplay) and mem is not wordplay.Wordplay}

		logger.debug('%s instance initialised.' % self.__class__.__name__)


	def parseClue(self, clue, length=None, typ=None, known_letters=None, brute_force=False, **kwargs):
		"""
		This is the core method that handles input clues, interprets them, then passes them off to other
		 modules to dissect. It then re-assimilates all solutions, sorts them, then returns them to the user.
		"""

		logger.info('Parsing clue: %s' % clue)

		# Convert to Clue object if it is not already.
		if not isinstance(clue, Clue):
			clue = Clue(clue, length, typ, known_letters)
			logger.debug('Converted clue to Clue object: %s' % clue)

		# Loop through all possible definitions.
		solutions = []
		raw_solns = set() # for bruteforcing later
		raw_definitions = [] # for bruteforcing later
		for defpos in filter(lambda x: x!=0, range(-DEFINITION_MAX_LEN, DEFINITION_MAX_LEN+1)):

			# Generate a list of possible solutions for chosen definition.
			# Defpos signifies how many words in the definition.
			# A negative value indicates to take words from end of string.
			definition = '_'.join(clue.tokens[0 if defpos > 0 else defpos : defpos if defpos > 0 else None])
			if not wordnet.exists(definition):
				continue

			raw_definitions.append([defpos,definition])

			# Generate possible wordplay interpretations. (Convert to a tree structure with keywords at nodes.)
			wpTokens = clue.tokens[0 if defpos < 0 else defpos:defpos if defpos < 0 else None]
			interpretations = self.interpret(clue, wpTokens)
			# Consider each interpretation.
			for kwpos, typs in interpretations.items():
				for typ, subplay in typs.items():
					if self.gui_thread:
						if self.gui_thread.halt():
							return solutions
						self.gui_thread.updateStatus(typ=typ)
					for soln in self.wordplays[typ].check(clue, subplay, wordplays=self.wordplays, gui=self.gui_thread, **kwargs):
						if self.gui_thread and self.gui_thread.halt():
							return solutions
						certainty = wordnet.calcSimilarity(soln.solution, definition) * soln.certainty
						if certainty > 0:
							solutions.append(
									Solution(clue,
												soln.solution,
												defpos,
												[(kwpos + (defpos if defpos > 0 else 0)) if kwpos >= 0 else -1, typ,
													' '.join(soln.applied_to)],
												certainty
									)
							)
							raw_solns.add(soln.solution)

		# Sort solutions by certainty score.
		solutions = sorted(solutions, key=lambda s: s.certainty, reverse=True)

		# Consider brute-forcing solutions.
		if brute_force:
			if known_letters is None:
				raise BruteForceWithoutKnownLettersException
			if self.gui_thread:
				if self.gui_thread.halt():
					return solutions
				self.gui_thread.updateStatus(typ='brute-forcing')
			# Get a brute-forced list of solutions.
			brute_solns = set(wordnet.getWordsWithPattern(clue.regex)) - raw_solns
			brute_forced_solutions = []
			for soln in brute_solns:
				if self.gui_thread and self.gui_thread.halt():
					return solutions
				soln_certainty = max([(0,None)]+[(wordnet.calcSimilarity(soln, d[1]), d[0]) for d in raw_definitions], key=lambda x:x[0])
				brute_forced_solutions.append(
						Solution(clue,
									soln,
									soln_certainty[1] if soln_certainty[0] > 0 else None,
									[-1, 'brute-forced',	'---'],
									soln_certainty[0]
						)
				)
			solutions.extend(sorted(brute_forced_solutions, key=lambda s: s.certainty, reverse=True))

		if solutions:
			logger.info('%i solution(s) found. Best solution is \'%s\' (certainty: %f)' % (len(solutions), solutions[0].solution, solutions[0].certainty))
		else:
			logger.info('Unsuccessful in resolving clue.')
		return solutions


	def interpret(self, clue, wp_tokens):
		"""
		Generates a list of possible interpretations for the wordplay part.
		"""
		kwords = {}
		for pos, word in enumerate(wp_tokens):
			word = wordnet.stemmer.stem(word)
			try:
				if word in self.wordplays[clue.typ].keywords:
					kwords[pos] = [clue.typ]
			except KeyError:
				# No wordplay type provided; attempt to fit each wordplay.
				for typ, wp in self.wordplays.items():
					if word in wp.keywords:
						kwords.setdefault(pos, []).append(typ)

		# Assume only single-keyword wordplays.
		interpretations = {}
		for pos, typs in kwords.items():
			interpretations[pos] = {}
			for typ in typs:
				interpretations[pos][typ] = {}
				# Consider token sets before and after the keyword.
				interpretations[pos][typ] = {'<': wp_tokens[:pos], '>': wp_tokens[pos + 1:]}

		# Add wordplays which do not use keywords
		interpretations[-1] = {}
		if clue.typ is not None:
			if not self.wordplays[clue.typ].usesKeywords:
				interpretations[-1][clue.typ] = wp_tokens
		else:
			for typ, wp in self.wordplays.items():
				if not wp.usesKeywords:
					interpretations[-1][typ] = wp_tokens

		return interpretations

	def recompileDictionaries(self, **kwargs):
		"""
		Recompiles all of the custom wordplay dictionaries.
		"""

		for wp in self.wordplays.values():
			if wp.hasCustomDict:
				wp.recompileDictionary(**kwargs)

	def recompileWordlist(self, **kwargs):
		"""
		Recompiles the wordlist, followed by all of the custom wordplay dictionaries.
		"""

		wordnet.recompileWordList(**kwargs)
		self.recompileDictionaries(**kwargs)
