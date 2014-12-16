# -*- coding: utf-8 -*-

"""
A wrapper module for NLTK WordNet, which encapsulates and simplifies the key functionality of interest.
This includes:
	-access to a dedicated wordlist (coupled with a function to check if a given word exists within this list)
	-plurality checking
	-plural generation
	-word stemming
	-word pair similarity calculation
	-synonym generation
	-word abbreviation
	-pattern matching (returning words in the wordlist that match a given pattern)
"""

# Python libraries
import sys
from itertools import product
from glob import glob  # library for retrieving file name lists from directories
import re  # regex library
import pdb

# Dictionary libraries
import nltk
nltk.data.path.append('dict/nltk_data')
from nltk.corpus import wordnet as wn # Source code: http://www.nltk.org/_modules/nltk/corpus/reader/wordnet.html
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import inflect

# Other CCS modules
import log  # module for giving runtime feedback to the user

__author__ = 'Jarek Glowacki'
logger = log.getLogger(__name__, streamLevel=log.DEBUG)
stemmer = PorterStemmer()
lemmatiser = WordNetLemmatizer()
pluraliser = inflect.engine()

def recompileWordList(cat_dir='dict/categorised/', comp_dir='dict/complete/'):
	"""
	Constructs and compiles a comprehensive fast-lookup word list to be used by various other parts of the CCS.
	"""

	# Read in any complete word lists.
	complete = set()
	for filename in glob(comp_dir + '*.txt'):
		with open(filename, 'r') as f:
			complete |= {line.rstrip() for line in f.readlines()}

	# Read in the categorised words.
	try:
		with open(cat_dir + 'nouns.txt', 'r') as f:
			nouns = {line.rstrip() for line in f.readlines()}
		with open(cat_dir + 'verbs.txt', 'r') as f:
			verbs = {line.rstrip() for line in f.readlines()}
		with open(cat_dir + 'adjectives.txt', 'r') as f:
			adjs = {line.rstrip() for line in f.readlines()}
		with open(cat_dir + 'adverbs.txt', 'r') as f:
			advs = {line.rstrip() for line in f.readlines()}
		with open(cat_dir + 'stopwords.txt', 'r') as f:
			stops = {line.rstrip() for line in f.readlines()}
	except FileNotFoundError as e:
		logger.critical('Missing base files required to rebuild word list: %s' % e)

	# Add inflections of the categorised words.
	inflections = set()
	for b in [True, False]:
		pluraliser.classical(all=b) # consider both classical and modern inflections.
		# WordNet uses '_' as word separator, but pyInflect uses '-'. Grrr..
		inflections |= {pluraliser.plural_noun(w.replace('_','-')).replace('-','_') for w in nouns}
		inflections |= {pluraliser.plural_verb(w.replace('_','-')).replace('-','_') for w in verbs}
		inflections |= {pluraliser.plural_adj(w.replace('_','-')).replace('-','_') for w in adjs}

	# Apply some CCS-specific filtering.
	words = set()
	for word in complete | nouns | verbs | adjs | advs | stops | inflections:
		word = word.lower().replace('-', '').replace('\'', '')
		if word.replace('_','').isalpha():
			words.add(word)

	global WORDLIST_SORTED
	global WORDLIST
	WORDLIST_SORTED = sorted(words)
	WORDLIST = words
	# Write the resulting list out to a file.
	with open('dict/wordlist.dic', 'w+') as f:
		f.writelines([word + '\n' for word in WORDLIST_SORTED])


def exists(word):
	""" Checks whether a given word exists in the dictionary."""

	return word in WORDLIST

def isPlural(word):
	""" Checks whether a given word is in plural form."""

	return word is not lemmatiser.lemmatize(word, 'n')

def pluralise(to_pluralise):
	"""
	Checks whether a given word is in plural form.
	NOTE: This does not check if words aren't already plurals! If they are, they will become singular again!
	"""


	if isinstance(to_pluralise, set):
		return {pluralise(word) for word in to_pluralise}
	if isinstance(to_pluralise, str):
		return pluraliser.plural(to_pluralise)
	# Assume list
	return [pluralise(word) for word in to_pluralise]


def literalStem(word):
	"""
	Applies a literal word stemming, which may occasionally change the sense of a word.
	Cryptic clues often play this sort of trickery.
	"""

	if word.endswith('y'):
		stripped = word.rstrip('y')
		if exists(stripped):
			return stripped
	return None


_SIM_CACHE = {}
def calcSimilarity(word1, word2):
	"""
	Computes a certainty score determining how similar two input words are to one another.
	Employs some basic caching to speed up repeated requests.
	"""

	word1, word2 = sorted([word1, word2])
	try:
		return _SIM_CACHE['%s,%s' % (word1, word2)]
	except KeyError:
		ss1 = wn.synsets(word1)
		ss2 = wn.synsets(word2)

		# Consider literal stems too (eg. gutsy -> guts).
		ls = literalStem(word1)
		if ls:
			ss1.extend(wn.synsets(ls))
		ls = literalStem(word2)
		if ls:
			ss2.extend(wn.synsets(ls))
		# Flush cache if it's getting too big
		if sys.getsizeof(_SIM_CACHE) > 50000000:
			_SIM_CACHE.clear()
			logger.debug('Flushed similarity cache!')
		_SIM_CACHE['%s,%s' % (word1, word2)] = _nmax(sim for sim in [_path_similarity(s1, s2) for (s1, s2) in product(ss1, ss2)])
		return _SIM_CACHE['%s,%s' % (word1, word2)]


_SYN_CACHE = {}
def getSynonyms(word, synonym_search_depth=2):
	"""
	Returns a list of words/phrases with similar meanings to the given word/phrase.
	These 'synonyms' are constructed from WordNet's synset, hypernym/hyponym,
	 and similar_to relations.
	The degree of separation threshold can be provided to specify how close
	 in meaning the synonyms are to be.
	Employs some basic caching to speed up repeated requests.
	"""

	try:
		return _SYN_CACHE[word + str(synonym_search_depth)]
	except KeyError:
		synsets = set(wn.synsets(word))
		plural = isPlural(word)
		synsets |= {sim for syn in synsets for sim in syn.similar_tos()}
		for i in range(synonym_search_depth):
			# Expand the set of hypernyms/hyponyms for the word of interest.
			hypernyms = {hyp for syn in synsets for hyp in syn.hypernyms()}
			hyponyms = {hyp for syn in synsets for hyp in syn.hyponyms()}

			# Pack them with similar words at each step.
			hypernyms |= {sim for hyp in synsets for sim in hyp.similar_tos()}
			hyponyms |= {sim for hyp in synsets for sim in hyp.similar_tos()}

			synsets |= hypernyms | hyponyms
		results = {lemma.lower() for syn in synsets for lemma in syn.lemma_names()}
		if plural:
			results = pluralise(results)
		# Flush cache if it's getting too big
		if sys.getsizeof(_SYN_CACHE) > 500000:
			_SYN_CACHE.clear()
			logger.debug('Flushed synonym cache!')
		_SYN_CACHE[word + str(synonym_search_depth)] = results
		return _SYN_CACHE[word + str(synonym_search_depth)]

_ABBREVIATION_LIST = {}
def getAbbreviations(word):
	"""
	Returns the abbreviations of a word if any exist in the abbreviation list.
	Loads in full abbreviation list when method first called.
	"""

	global _ABBREVIATION_LIST
	if not _ABBREVIATION_LIST:
		try:
			with open('keywords/abbreviations.kwords', 'r') as f:
				[_ABBREVIATION_LIST.setdefault(word, set()).add(ac) for ac,word in [line.rstrip(' *+\n').split(': ') for line in f.readlines()]]
		except FileNotFoundError:
			logger.error('Missing abbreviations list: \'keywords/%abbreviations.kwords\'')
			raise
	try:
		return _ABBREVIATION_LIST[word]
	except KeyError:
		return {}

def getWordsWithPattern(pattern):
	"""
	Returns all instances in the wordlist that match the given pattern.
	The pattern should be provided as a regular expression.
	"""

	results = []
	for word in WORDLIST_SORTED:
		if re.search(pattern, word):
			results.append(word)
	return results

###
# Some auxiliary functions.
###

# Custom 'max' function that ignore 'None' entries, and defaults to zero if empty.
def _nmax(v):
	return max([x for x in v if x is not None] + [0])

# WordNet's path_similarity() is not commutative (who knew!?); this function makes it so, optimistically.
def _path_similarity(x, y):
	return _nmax([x.wup_similarity(y), y.wup_similarity(x)])


###
# Load a comprehensive word list on import.
###
try:
	with open('dict/wordlist.dic', 'r') as wlist:
		WORDLIST_SORTED = [line.rstrip() for line in wlist.readlines()]
	WORDLIST = set(WORDLIST_SORTED)
except FileNotFoundError:
	logger.info('No pre-compiled word list present.. recompiling new one!')
	recompileWordList()