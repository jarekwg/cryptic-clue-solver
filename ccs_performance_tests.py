# -*- coding: utf-8 -*-
"""
Reads in a set of puzzles from the downloaded smh puzzles (motherlode) archive,
 parses them, and then feeds the clues one by one into the CCS to test its strength.
Note that this does not take advantage of solved clues to gain hints on unsolved clues;
 the purpose is merely to test the success rate of solving clues individually.
The first three solutions output from the CCS are matched against the true solution,
 with the resulting statistics logged at the end.
Note also that clues that hint at multi-word answers are skipped and not included in the score,
 however clues like 'See 7 across' have yet to be weeded out at this stage.
A score of 100% is not possible, as these puzzles contain clue types that the CCS does not and
 will not handle, however running this module several times during development and comparing
 the runs should give a rough indication of what progress has been made.
"""
# TODO: Weed out 'See 7 across' type clues.

# Python libraries
import glob  # library for retrieving file name lists from directories
import pdb  # live debugging module
import numpy as np  # numerical module for cleaner mutlidimensional array use

# Other CCS modules
from clue_parser import ClueParser
from exceptions import *  # custom CCS exceptions
import log  # module for giving runtime feedback to the user


__author__ = "Jarek Glowacki"
logger = log.getLogger(__name__, streamLevel=log.INFO)

###
# The below code is somewhat messy as it is not a part of the program, nor is it a unit/integration test
#  that needs to be run after any change. It's purpose is merely to get a rough idea of how many clues
#  the program can solve from a huge clue pool. BEWARE: Takes hours to finish!
###

MAX_FILES_TO_READ = 2000  # 1662 entries in current archive => 38621 clues.
PUZZLE_PATH = 'smh/'
GRID_LEN = 15
GRID_SIZE = GRID_LEN * GRID_LEN

BLACK = '.'
numRead = 0
numAttempted = 0
numCorrect = [0, 0, 0]  # first guess, second guess, third guess

cp = ClueParser()

for filename in glob.glob(PUZZLE_PATH + '*.puz'):
	# Open the file, ignoring encoding conversion errors.
	with open(filename, errors='ignore') as f:
		text = f.read().split('\x00')
	offset = 0
	while len(text[8 + offset]) < GRID_SIZE:
		offset += 1
	solved = text[8 + offset][0:GRID_SIZE]
	solvedGrid = np.array([list(solved[i:i + GRID_LEN]) for i in range(0, GRID_SIZE, GRID_LEN)])
	# unsolved = text[8][GRID_SIZE:GRID_SIZE*2]
	clues = [clue for clue in text[11 + offset:]]
	# for i in range(0, GRID_SIZE, GRID_LEN):
	#	print(solved[i:i+GRID_LEN])
	#for i in range(0, GRID_SIZE, GRID_LEN):
	#	print(unsolved[i:i+GRID_LEN])
	solns = []
	for i in range(0, GRID_LEN):
		for j in range(0, GRID_LEN):
			if solvedGrid[i, j] == BLACK:
				continue
			# Start of a horizontal word?
			if j == 0 or solvedGrid[i, j - 1] == BLACK:
				# Scan across to find its end
				k = j
				while k < GRID_LEN and solvedGrid[i, k] != BLACK:
					k += 1
				if k - j > 1:
					solns.append(''.join(solvedGrid[i, j:k]))
			# Start of a vertical word?
			if i == 0 or solvedGrid[i - 1, j] == BLACK:
				# Scan down to find its end
				k = i
				while k < GRID_LEN and solvedGrid[k, j] != BLACK:
					k += 1
				if k - i > 1:
					solns.append(''.join(solvedGrid[i:k, j]))

	#print('*'*30 + filename[-6:-4] + '*'*30)
	for i in range(len(solns)):
		logger.debug('Running clue: %s = %s' % (clues[i], solns[i]))
		try:
			result = cp.parseClue(clues[i])
		except UnsupportedClueException:
			logger.debug('Unsupported solution type.')
			continue
		numAttempted += 1
		for guessNo in range(3):
			try:
				logger.debug('Guess #%i: %s (certainty: %s)' % (guessNo+1, result[guessNo].solution.upper(), result[guessNo].certainty))
				if result[guessNo].solution.upper() == solns[i]:
					numCorrect[guessNo] += 1
					break # This is important, else other solutions with same string will artificially inflate the count.
			except IndexError:
				break

	numRead += 1
	if numRead >= MAX_FILES_TO_READ:
		break

logger.info('Attempted crossword clues from %i crosswords.' % numRead)
(a,b) = (numCorrect[0], numAttempted)
logger.info('Clues guessed correctly on first attempt: %i/%i (%.2f%%)' % (a, b, a/b * 100))
(a,b) = (numCorrect[1], numAttempted - numCorrect[0])
logger.info('Clues guessed correctly on second attempt: %i/%i (%.2f%%)' % (a, b, a/b * 100))
(a,b) = (numCorrect[2], numAttempted - numCorrect[0] - numCorrect[1])
logger.info('Clues guessed correctly on third attempt: %i/%i (%.2f%%)' % (a, b, a/b * 100))