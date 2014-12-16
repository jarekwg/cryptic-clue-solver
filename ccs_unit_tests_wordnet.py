__author__ = 'Jarek Glowacki'

import unittest

import wordnet

class UnitTestsWordnet(unittest.TestCase):
	"""
	These tests check whether the custom WordNet wrapper is behaving as required.
	"""

	def test_loadingWordlist(self):
		self.assertTrue(len(wordnet.WORDLIST) > 0, 'Wordlist (set) not loaded!')
		self.assertTrue(len(wordnet.WORDLIST_SORTED) > 0, 'Wordlist (list) not loaded!')

	def test_existence(self):
		for word in ['cryptic', 'crosswords', 'are', 'neat']:
			self.assertTrue(wordnet.exists(word), '\'%s\' is not in wordlist!' % word)

	def test_non_existence(self):
		for word in ['spellling', 'ish', 'veary', 'impoortent']:
			self.assertFalse(wordnet.exists(word), '\'%s\' should not be in wordlist!' % word)

	def test_plurality(self):
		for word in ['lasts', 'minutes', 'assignments', 'submissions', 'whiners']:
			self.assertTrue(wordnet.isPlural(word), '\'%s\' is not being considered as plural!' % word)

	def test_non_plurality(self):
		for word in ['effort', 'sweat', 'blood', 'work', 'fun']:
			self.assertFalse(wordnet.isPlural(word), '\'%s\' is being considered as plural!' % word)

	def test_pluralisation(self):
		for pair in [('man','men'), ('cloud', 'clouds'), ('fish', 'fish')]:
			self.assertEqual(wordnet.pluralise(pair[0]), pair[1], '\'%s\' is being incorrectly pluralised!' % pair[0])

	def test_similarity(self):
		for pair in [('frog','tadpole'), ('cool', 'chilly'), ('planet', 'earth')]:
			self.assertGreater(wordnet.calcSimilarity(pair[0], pair[1]), 0.4, '\'%s\' is not considered sufficiently similar to \'%s\'!' % (pair[0], pair[1]))

	def test_synonymGeneration(self):
		for pair in [('mother','mum'), ('carpet', 'rug'), ('drapes', 'curtains')]:
			self.assertTrue(pair[0] in wordnet.getSynonyms(pair[1]), '\'%s\' is not considered a synonym of \'%s\'!' % (pair[0], pair[1]))

	def test_abbreviationGeneration(self):
		for pair in [('w','woman'), ('l', 'left'), ('n', 'north')]:
			self.assertTrue(pair[0] in wordnet.getAbbreviations(pair[1]), '\'%s\' is not considered an abbreviation of \'%s\'!' % (pair[0], pair[1]))

	def test_patternCompletion(self):
		for pair in [('cot', 'c?t'), ('obsolete', 'ob????t?'), ('north', 'n????')]:
			self.assertTrue(pair[0] in wordnet.getWordsWithPattern('\A' + pair[1].replace('?','[a-z]') + '\Z'), '\'%s\' is not found to match \'%s\'!' % (pair[0], pair[1]))

