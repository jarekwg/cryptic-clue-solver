__author__ = 'Jarek Glowacki'

import unittest

import wordplay

class UnitTestsWordnet(unittest.TestCase):
	"""
	These tests check whether the wordplay module has well-behaved objects.
	Most of the functionality is already tested by the integration tests.
	This serves merely to fill in some gaps.
	"""

	def test_anagramWordplay(self):
		wp = wordplay.AnagramWordplay()
		self.assertTrue(len(wp.dictionary) > 0, '%s dictionary not loaded!' % wp.__typ__.capitalize())
		self.assertTrue(len(wp.keywords) > 0, '%s keywords not loaded!' % wp.__typ__.capitalize())

		for pair in [('magnate','magenta'), ('daffodil', 'lidoffda'), ('pots', 'stop')]:
			self.assertTrue(pair[0] in wp.getPlay(pair[1]), '\'%s\' is not considered an anagram of \'%s\'!' % (pair[0], pair[1]))


	def test_runWordplay(self):
		wp = wordplay.RunWordplay()
		self.assertTrue(len(wp.dictionary) > 0, '%s dictionary not loaded!' % wp.__typ__.capitalize())
		self.assertTrue(len(wp.keywords) > 0, '%s keywords not loaded!' % wp.__typ__.capitalize())

		for pair in [('obsolete',['job', 'sole', 'technician']), ('chariot', ['punch', 'a', 'rio', 'tinto']), ('post', ['lipo', 'stemography'])]:
			self.assertTrue(pair[0] in [w[0] for w in wp.getPlay(pair[1])], '\'%s\' is not considered a run of \'%s\'!' % (pair[0], pair[1]))

	# The remaining wordplays are too deeply intertwined with other modules to test here. They get sufficiently tested in the integration tests though.