# -*- coding: utf-8 -*-

"""
This module encompasses all of the currently accepted wordplay types.
These include:
	-anagrams
	-runs
	-double definitions
	-charades
	-initials
	-finals
In the case of charades, nested wordplays are considered, where initials, finals, abbreviations and synonyms
are checked for each half of the charade.
These modules generate list of solutions, and score each of them according to their own unique scoring algorithms.
"""

# TODO: Implement Reversals, Containers, Deletions and Homophones.

# Python libraries
import pickle  # module for reading/writing python objects from/to files
from itertools import chain, combinations, islice
from bisect import bisect_left # function for performing binary search
import pdb  # live debugging module

# Dictionary libraries
import wordnet # custom wrapper around NLTK WordNet

# Other CCS modules
import log  # module for giving runtime feedback to the user
from solution import WordplaySolution

__author__ = 'Jarek Glowacki'
logger = log.getLogger(__name__, streamLevel=log.INFO)


class Wordplay(object):
	"""
	Abstract Wordplay subclass from which all other wordplay classes stem.
	It focuses around the secretarial work of loading in keyword libraries and generating custom word lists.
	"""
	hasCustomDict = False
	usesKeywords = False
	__typ__ = None
	keywords = set()

	def __init__(self):
		# Load custom formatted dictionary if one exists.
		if self.hasCustomDict:
			try:
				self.dictionary = pickle.loads(open('dict/custom/%ss.dic' % self.__typ__, 'rb').read())
			except FileNotFoundError:
				logger.info('No pre-compiled %s dictionary present.. recompiling new one!' % self.__typ__)
				self.recompileDictionary()
			except UnicodeDecodeError:
				logger.warn('Pre-compiled %s dictionary appears to be corrupted.. recompiling new one!' % self.__typ__)
				self.recompileDictionary()

		# Load keyword list.
		if self.usesKeywords:
			try:
				self.keywords = {k.rstrip() for k in open('keywords/%ss.kwords' % self.__typ__, 'r').readlines()}
			except FileNotFoundError:
				logger.error('Missing keywords list: \'keywords/%ss.kwords\'' % self.__typ__)
				raise

		logger.debug('%s instance initialised.' % self.__class__.__name__)

	def getCombinations(self,tokens):
		"""
		Generate a list of plausible combinations of the available tokens.
		"""

		return list(set(chain(*map(lambda x: combinations(tokens, x), range(0, len(tokens)+1)))))

	def check(self, clue, tokens, **kwargs):
		raise NotImplementedError  # subclass must implement this

	def getPlay(self, **kwargs):
		raise NotImplementedError  # subclass must implement this

	def addToDictionary(self, word):
		raise NotImplementedError  # relevant subclasses must implement this

	def recompileDictionary(self, wordlist=wordnet.WORDLIST):
		"""
		Updates the Anagram and Run dictionaries from a given dict file.
		See dictionaries in dict/ folder for an example of the required format.
		The results are saved back to the dict/custom directory so that they
		don't have to be recompiled at the start of each run.
		"""

		self.dictionary = {}
		# Add words to dictionary.
		[self.addToDictionary(word) for word in wordlist]

		# Write the results to a text file for pre-loading in the future.
		with open('dict/custom/%ss.dic' % self.__typ__, 'wb+') as f:
			pickle.dump(self.dictionary, f)
		logger.debug('Recompiled %s dictionary!' % self.__typ__)


class AnagramWordplay(Wordplay):
	"""
	The anagram wordplay class. Generates and scores possible anagram wordplays.
	"""

	hasCustomDict = True
	usesKeywords = True
	__typ__ = 'anagram'

	def check(self, clue, token_sets, wordplays=None, **kwargs):
		anagrams = []
		# Combine all tokens that were on either side of the keyword.
		tokens = [token for token_set in token_sets.values() for token in token_set]
		for tv in [tokens]: #TODO: create token variations using abbreviations, initials and finals.
			for combo in self.getCombinations(tv):
				for soln in [s for s in self.getPlay(''.join(combo)) if clue.checkSolution(s)]:
					# TODO: Somehow append subplay to solution if one was used.
					anagrams.append(WordplaySolution(soln, self.__typ__, combo, self.calcCertainty(len(combo),len(tokens))))
			logger.debug('Anagram solutions found: %s' % anagrams)
		return anagrams

	def calcCertainty(self, num_tokens_used, num_tokens_available):
		"""
		Attempt to gauge how good the wordplay solution is based on how many of the available tokens it uses.
		"""

		# Subtract 10% certainty per word not used, up to 50%.
		return max(0.5, 1.0 - (num_tokens_available - num_tokens_used) * 0.1)

	def getPlay(self, string):
		"""
		Returns a list of anagrams for the given string.
		Relies on a pre-made dictionary of anagrams, which reduces the time
		complexity of this problem to that of a simple lookup.
		"""

		try:
			return self.dictionary[''.join(sorted(string))]
		except KeyError:
			return set()

	def addToDictionary(self, word):
		# Group words by common letters, sorted in alphabetical order.
		self.dictionary.setdefault(''.join(sorted(word)), set()).add(word)


class RunWordplay(Wordplay):
	"""
	The run wordplay class. Generates and scores possible run wordplays.
	"""

	hasCustomDict = True
	usesKeywords = True
	__typ__ = 'run'

	def check(self, clue, token_sets, **kwargs):
		runs = []
		for tokens in token_sets.values():
			for soln, tokensUsed in [(s,t) for s,t in self.getPlay(tokens) if clue.checkSolution(s)]:
				runs.append(WordplaySolution(soln, self.__typ__, tokensUsed, self.calcCertainty(len(tokensUsed),len(tokens))))
			logger.debug('Run solutions found: %s' % runs)
		return runs

	def calcCertainty(self, num_tokens_used, num_tokens_available):
		"""
		Attempt to gauge how good the wordplay solution is based on how many of the available tokens it uses.
		"""

		# Subtract 30% if soln uses only one token, and an additional 8% per token not used, with a one token buffer.
		# Max subtracted caps at 40%.
		return max(0.4, (1.0 if num_tokens_used > 1 else 0.7) - max((num_tokens_available - num_tokens_used - 1), 0) * 0.08)

	def findTokensUsed(self, start, end, tokens):
		""" Determines which tokens the run passed through. """

		tokenLengths = [len(t) for t in tokens]
		i = 0
		pos = 0
		while i <= start:
			i += tokenLengths[pos]
			pos += 1
		tokensUsed = [tokens[pos-1]]
		while i < end:
			i += tokenLengths[pos]
			tokensUsed.append(tokens[pos])
			pos += 1
		return tokensUsed

	def getPlay(self, tokens):
		"""
		Returns a list of all runs present in the given string.
		Relies on a pre-made dictionary of runs, which reduces the time
		complexity of this computation.
		"""

		string = ''.join(tokens)
		runs = []
		# For each possible starting point in string.
		for i in range(len(string)):
			# Traverse tree for valid words
			pos = self.dictionary
			for j in range(i, len(string)):
				try:
					pos = pos[string[j]]
				except KeyError:
					# No more valid words exist from hereon
					break
				if '~' in pos:
					# Point up to and including current letter forms a word.
					runs.append([string[i:j+1], self.findTokensUsed(i, j+1, tokens)])
		return runs

	def addToDictionary(self, word):
		# Store words in a tree structure, with a letter per node.
		pos = self.dictionary
		for letter in word:
			pos = pos.setdefault(letter, {})
		pos['~'] = None  #store a word terminator

class DoubleDefinitionWordplay(Wordplay):
	"""
	The double definition wordplay class. Generates and scores possible double definitions wordplays.
	"""
	__typ__ = 'double definition'

	def check(self, clue, tokens, synonym_search_depth=1, gui=None, **kwargs):
		definitions = []
		for combo in self.getContiguousCombinations(tokens):
			second_definition = '_'.join(combo)
			for soln in [s for s in wordnet.getSynonyms(second_definition, synonym_search_depth) if clue.checkSolution(s)]:
				if gui and gui.halt():
					return definitions
				certainty = self.calcCertainty(len(combo),len(tokens)) * wordnet.calcSimilarity(second_definition, soln)
				definitions.append(WordplaySolution(soln, self.__typ__, combo, certainty))
		logger.debug('Double definition solutions found: %s' % definitions)
		return definitions

	def calcCertainty(self, num_tokens_used, num_tokens_available):
		"""
		Attempt to gauge how good the wordplay solution is based on how many of the available tokens it uses.
		"""

		# Subtract 15% certainty per word not used, up to 60%.
		return max(0.4, 1.0 - (num_tokens_available - num_tokens_used) * 0.15)

	def getContiguousCombinations(self, tokens):
		numTokens = len(tokens)
		combos = []
		if numTokens <= 3: # If there's more than three tokens, then it's not a definition that we can handle.
			for i in range(numTokens):
				for j in range(i+1,numTokens+1):
					combos.append(tokens[i:j])
		return combos

class CharadeWordplay(Wordplay):
	"""
	The charade wordplay class. Generates and scores possible charade wordplays.
	This is by far the most complex class, and it consumes a huge portion of the total processing time.
	"""

	__typ__ = 'charade'
	usesKeywords = False # Charades MAY use keywords, but don't have to, so we'll check for them internally.

	# TODO: Have charades return information on the subplays of the respective parts (eg. "<charade(syn|abbr)>")

	def check(self, clue, tokens, wordplays=None, gui=None, **kwargs):
		#pdb.set_trace()
		num_tokens = len(tokens)
		# A charade must have at least two tokens.
		if num_tokens < 2:
			return []

		charades = []
		# TODO: Maybe there is a keyword here that we can use ('with', 'after', 'follwed by', etc)?
		# Consider each possible way of breaking up the tokens into two sets.
		for pos in range(1,num_tokens):
			left = tokens[:pos]
			right = tokens[pos:]
			play_solns = self.getPlay(left, right, clue.length, wordplays, gui)
			for (soln, certainty) in [(s, c) for (s, c) in play_solns if clue.checkSolution(s)]:
				charades.append(WordplaySolution(soln, self.__typ__, tokens, certainty))
		logger.debug('Charade solutions found: %s' % charades)
		return charades

	def getPlay(self, left, right, length=None, wordplays=None, gui=None):

		charades = []
		possible_lefts = [] # consist of word-certainty pairs
		possible_rights = [] # consist of just words (more convenient this way)
		# Check if any possible code keywords exist in either part.
		if wordplays is not None:
			for typ in ['initial', 'final']:
				try:
					for pos, word in enumerate(left):
						word = wordnet.stemmer.stem(word)
						if word in wordplays[typ].keywords:
							if len(left[:pos]) > 0:
								possible_lefts.append((wordplays[typ].getPlay(left[:pos]),1.0))
							if len(left[pos+1:]) > 0:
								possible_lefts.append((wordplays[typ].getPlay(left[pos+1:]),1.0))
				except KeyError:
					pass
				try:
					for pos, word in enumerate(right):
						word = wordnet.stemmer.stem(word)
						if word in wordplays[typ].keywords:
							if len(right[:pos]) > 0:
								possible_rights.append(wordplays[typ].getPlay(right[:pos]))
							if len(right[pos+1:]) > 0:
								possible_rights.append(wordplays[typ].getPlay(right[pos+1:]))
				except KeyError:
					pass

		# Add any abbreviations to the mix
		if len(left) == 1:
			possible_lefts.extend([(a, 1.0) for a in wordnet.getAbbreviations(left[0])])
		if len(right) == 1:
			possible_rights.extend(wordnet.getAbbreviations(right[0]))

		left, right = ('_'.join(left), '_'.join(right))
		# Try synonyms too
		if wordnet.exists(left):
			possible_lefts.extend([(s, -1.0) for s in wordnet.getSynonyms(left) if len(s.split('_'))==1])

		for possible_left, lsim in possible_lefts:
			for possible_right, rsim in [(pr, wordnet.calcSimilarity(pr, right))\
					for pr in self.getPossibleRights(possible_left, length) if wordnet.exists(pr)] +\
					[(pr, 1.0) for pr in possible_rights if wordnet.exists(possible_left + pr)]:
				if gui and gui.halt():
					return charades
				if rsim > 0:
					if lsim < 0:
						# Wait till now to compute this, as earlier we weren't sure if it'd get used.
						lsim = wordnet.calcSimilarity(possible_left, left)
					charades.append((possible_left+possible_right, rsim * lsim))
		return charades

	def getPossibleRights(self, left, length=None):

		# TODO: Find a solution to the really computation heavy requests of one- or two-letter lefts.

		len_left = len(left)
		# Traverse the RunWordplayDictionary
		# Grab a slice of the sorted wordlist that starts from the word of interest
		for w in islice(wordnet.WORDLIST_SORTED,bisect_left(wordnet.WORDLIST_SORTED, left), None):
			# Output 'rights' of results until they no longer start with the desired 'left'.
			if w[0:len_left]==left:
				if length is not None and len(w) != length:
					continue
				yield w[len_left:].replace('_','')
			else:
				break

class InitialWordplay(Wordplay):
	"""
	The initial wordplay class. Generates and scores possible initial wordplays.
	"""
	usesKeywords = True
	__typ__ = 'initial'

	def check(self, clue, token_sets, **kwargs):
		initials = []
		tokens = [token for token_set in token_sets.values() for token in token_set]
		for combo in self.getCombinations(tokens):
			soln = self.getPlay(combo)
			if wordnet.exists(soln) and clue.checkSolution(soln):
				initials.append(WordplaySolution(soln, self.__typ__, combo, self.calcCertainty(len(combo),len(tokens))))
		logger.debug('Initial solutions found: %s' % initials)
		return initials

	def calcCertainty(self, num_tokens_used, num_tokens_available):
		"""
		Attempt to gauge how good the wordplay solution is based on how many of the available tokens it uses.
		"""

		# Subtract 10% certainty per word not used, up to 50%.
		return max(0.5, 1.0 - (num_tokens_available - num_tokens_used) * 0.1)

	def getPlay(self, tokens):
		return ''.join([t[0] for t in tokens])

class FinalWordplay(Wordplay):
	"""
	The final wordplay class. Generates and scores possible final wordplays.
	It seems fitting for this wordplay to be the last one in this module.
	"""
	usesKeywords = True
	__typ__ = 'final'

	def check(self, clue, token_sets, **kwargs):
		finals = []
		tokens = [token for token_set in token_sets.values() for token in token_set]
		for combo in self.getCombinations(tokens):
			soln = self.getPlay(combo)
			if wordnet.exists(soln) and clue.checkSolution(soln):
				finals.append(WordplaySolution(soln, self.__typ__, combo, self.calcCertainty(len(combo),len(tokens))))
		logger.debug('Final solutions found: %s' % finals)
		return finals

	def calcCertainty(self, num_tokens_used, num_tokens_available):
		"""
		Attempt to gauge how good the wordplay solution is based on how many of the available tokens it uses.
		"""

		# Subtract 10% certainty per word not used, up to 50%.
		return max(0.5, 1.0 - (num_tokens_available - num_tokens_used) * 0.1)

	def getPlay(self, tokens):
		return ''.join([t[-1] for t in tokens])
