__author__ = 'Jarek Glowacki'
import timeit
import numpy as np
###################################################
function = 'wordnet.exists'
setup = """
import wordnet

def test():
	wordnet.exists('troubadour')
"""
repetitions = 1000000
print("Average time to execute function '%s' is %.3fus" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(10, repetitions))/repetitions*1000000))
###################################################

function = 'wordnet.calcSimilarity'
setup = """
import wordnet

def test():
	wordnet.calcSimilarity('troubadour', 'valkyrie')
"""
repetitions = 10000
print("Average time to execute function '%s' is %.3fms" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(repetitions, 1))*1000))
###################################################

function = 'wordnet.getSynonyms'
setup = """
import wordnet

def test():
	wordnet.getSynonyms('parsnip')
"""
repetitions = 1000000
print("Average time to execute function '%s' is %.3fus" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(repetitions, 1))*1000000))
###################################################

function = 'wordnet.getAbbreviations'
setup = """
import wordnet

def test():
	wordnet.getAbbreviations('tungsten')
"""
repetitions = 1000000
print("Average time to execute function '%s' is %.3fus" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(repetitions, 1))*1000000))
###################################################

function = 'wordnet.getWordsWithPattern'
setup = """
import wordnet

def test():
	wordnet.getWordsWithPattern('\A[a-z][a-z][a-z]i[a-z]a\Z')
"""
repetitions = 10
print("Average time to execute function '%s' is %.3fms" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(repetitions, 1))*1000))
###################################################

function = 'wordplay.getAnagrams'
setup = """
from clue_parser import ClueParser
cp = ClueParser()
ana = cp.wordplays['anagram']

def test():
	ana.getPlay('pots')
"""
repetitions = 100000
print("Average time to execute function '%s' is %.3fus" % (function, np.mean(timeit.Timer('test()', setup=setup).repeat(10, repetitions))/repetitions*1000000))
###################################################