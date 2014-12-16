# -*- coding: utf-8 -*-

"""
The top-level module that controls the GUI and generates queries to CCS as required.
"""

import sys
import pdb
import numpy as np # for sign function
from time import sleep
from types import MethodType
from PyQt4 import QtGui, QtCore, uic
from clue_parser import ClueParser
from exceptions import SolutionLengthMismatchException, BruteForceWithoutKnownLettersException

__author__ = 'Jarek Glowacki'

# TODO: Add connections for wordlist/custom-wordlist recompilation to status bar.

DEBUG = False# True
class STATUS():
	ERROR_BRUTEFORCEWHAT = -2
	ERROR_SOLNMISMATCH = -1
	INITIALISING = 0
	READY = 1
	PROCESSING = 2
	FINISHED = 3
	TERMINATED_EARLY = 4
	OTHER = 5

class CCSThread(QtCore.QThread):
	"""
	This is an abstract wrapper class around Qt thread objects.
	Using threads makes the GUI more responsive, so that it doesn't freeze when solutions are being computed.
	"""

	statusUpdate = QtCore.pyqtSignal(int, dict)

	def __init__(self, main):
		QtCore.QThread.__init__(self)
		self.main = main

	def updateStatus(self, status=STATUS.OTHER, **kwargs):
		self.statusUpdate.emit(status, kwargs)
		sleep (0.1)

class CCSInit(CCSThread):
	""" This thread has the important task of initialising the CCS clue parser. """

	def run(self):
		self.updateStatus(STATUS.INITIALISING)
		self.main.cp = ClueParser(self.main.ccsParseClue)
		self.updateStatus(STATUS.READY)

class CCSParseClue(CCSThread):
	""" This thread runs each time a clue is submitted for parsing via the GUI. """

	solutionsToDisplay = QtCore.pyqtSignal(int, list)

	def run(self):
		self.updateStatus(STATUS.PROCESSING)
		try:
			solns = self.main.cp.parseClue(synonym_search_depth=self.main.slrSynSearchDepth.value(), **self.main.clueKwargs)
		except SolutionLengthMismatchException:
			self.updateStatus(STATUS.ERROR_SOLNMISMATCH)
			return
		except BruteForceWithoutKnownLettersException:
			self.updateStatus(STATUS.ERROR_BRUTEFORCEWHAT)
			return
		if self.halt():
			self.solutionsToDisplay.emit(STATUS.TERMINATED_EARLY, solns)
		else:
			self.solutionsToDisplay.emit(STATUS.FINISHED, solns)

	def halt(self):
		return self.main.halt

class CCSMain(QtGui.QMainWindow):
	"""
	This is the class responsible for controlling everything that happens in the GUI.
	It sets up all signal/slot connections, handles all trivial signals directly, and delegates the heavier computation
	 to other threads, so that the GUI can remain responsive.
	"""

	def __init__(self):
		super(CCSMain, self).__init__()
		uic.loadUi('GUI/ccs.ui', self)
		self.clueKwargs = {}
		self.halt = False

		# Setup the other threads.
		self.ccsParseClue = CCSParseClue(self)
		self.ccsParseClue.statusUpdate.connect(self.updateStatus)
		self.ccsParseClue.solutionsToDisplay.connect(self.printSolutions)
		self.ccsInit = CCSInit(self)
		self.ccsInit.statusUpdate.connect(self.updateStatus)
		self.ccsInit.start()

		# Setup additional signal/slot connections which could not be included in the ui description file.
		QtCore.QObject.connect(self.btnParseClue, QtCore.SIGNAL("clicked()"), self.parseClue)
		QtCore.QObject.connect(self.btnCancel, QtCore.SIGNAL("clicked()"), self.cancel)
		QtCore.QObject.connect(self.btnDebug, QtCore.SIGNAL("clicked()"), self.debug)

		# Setup 'intuitiveness' connections, to ensure that all elements in the form work together and validate
		#  user input dynamically.
		QtCore.QObject.connect(self.txtKnownLetters, QtCore.SIGNAL("textChanged(QString)"), self.handleKnownLettersChanged)
		QtCore.QObject.connect(self.gpbWordLength, QtCore.SIGNAL("toggled(bool)"), self.handleWordLengthToggled)
		QtCore.QObject.connect(self.slrWordLength, QtCore.SIGNAL("sliderMoved(int)"), self.handleWordLengthChanged)
		self.txtKnownLetters.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-zA-Z\?]*'), self.txtKnownLetters))
		if not DEBUG:
			self.btnDebug.hide()
		self.btnCancel.hide()

		# Apply a mouse scroll fix override (see scrollFix function for details).
		self.lstSolns.wheelEvent = MethodType(scrollFix, self.lstSolns)

		# Show the form!
		self.show()

	def updateStatus(self, status=None, kwargs={}):
		"""
		This method handles incoming 'status' updates and passes them onto the user via either the status bar
		 or message boxes.
		"""
		if status == STATUS.INITIALISING:
			self.statusBar().showMessage('Initialising...')
			self.btnParseClue.setEnabled(False)
		elif status == STATUS.READY:
			self.statusBar().showMessage('Ready.')
			self.btnParseClue.setEnabled(True)
		elif status == STATUS.PROCESSING:
			self.statusBar().showMessage('Processing clue...')
			self.btnParseClue.setEnabled(False)
			self.btnParseClue.hide()
			self.btnCancel.show()
		elif status == STATUS.FINISHED:
			self.statusBar().showMessage('%i result%s found.' %(kwargs['num_results'], 's' if kwargs['num_results'] == 0 else ''))
			self.btnParseClue.setEnabled(True)
			self.btnParseClue.show()
			self.btnCancel.hide()
		elif status == STATUS.TERMINATED_EARLY:
			self.statusBar().showMessage('%i result%s found - terminated early by user.' %(kwargs['num_results'], 's' if kwargs['num_results'] == 0 else ''))
			self.btnParseClue.setEnabled(True)
			self.btnParseClue.show()
			self.btnCancel.setEnabled(True)
			self.btnCancel.hide()
		elif status == STATUS.ERROR_SOLNMISMATCH:
			QtGui.QMessageBox.warning(self, "Clue Input Error",  "Two non-matching word lengths provided!\nEnter the word length either alongside the clue or using the options on the right, not both.")
			self.statusBar().showMessage('No results found - input error.')
			self.btnParseClue.setEnabled(True)
			self.btnParseClue.show()
			self.btnCancel.hide()
		elif status == STATUS.ERROR_BRUTEFORCEWHAT:
			QtGui.QMessageBox.warning(self, "Clue Input Error",  "Brute-force checkbox was ticked with no known letters provided!\nEnter known letters before attempting to brute-force solutions.")
			self.statusBar().showMessage('No results found - input error.')
			self.btnParseClue.setEnabled(True)
			self.btnParseClue.show()
			self.btnCancel.hide()
		elif status == STATUS.OTHER:
			try:
				if kwargs['typ'] == 'brute-forcing':
					self.statusBar().showMessage('Brute-forcing solutions...')
				else:
					self.statusBar().showMessage('Generating %s wordplays...' % kwargs['typ'])
			except KeyError:
				pass

	def parseClue(self):
		""" Sets up the relevant data for processing a parseClue request before handing it off to a worker thread. """

		# Prepare clue text
		clue = self.txtClueEntry.text()
		# Prepare solution length
		length=None
		if self.gpbWordLength.isChecked():
			length = self.slrWordLength.value()
		# Prepare wordplay selection.
		typ = None
		for rdb in self.grpWordplayTypes.buttons():
			if rdb.isChecked():
				typ = rdb.text().lower()
				if typ == 'any':
					typ = None
		# Prepare known letters.
		known_letters = self.txtKnownLetters.text()
		if known_letters == '':
			known_letters = None
		brute_force = self.chkBruteForce.isChecked()
		# Clear the solution list and re-populate it.
		self.lstSolns.clear()
		self.clueKwargs = {'clue': clue, 'length': length, 'typ': typ, 'known_letters': known_letters, 'brute_force': brute_force}
		self.halt = False
		self.ccsParseClue.start()

	def cancel(self):
		""" Cancels the current run prematurely. """
		self.halt = True
		self.btnCancel.setEnabled(False)

	def printSolutions(self, status, solns):
		""" Populates the solutions list box. """

		self.lstSolns.addItems([str(soln) for soln in solns])

		# Scroll back to top of list box.
		self.lstSolns.verticalScrollBar().setValue(0)
		self.updateStatus(status, {'num_results': len(solns)})

	def debug(self):
		""" Allows the user to trigger debugging mode from the UI. """

		pdb.set_trace()

	###
	# Additional GUI fanciness/intuitiveness.
	###

	def handleKnownLettersChanged(self, string):
		""" Updates other fields in the form when known letters are entered, along with filtering the input. """

		# Save the cursor position to restore it after changing the text.
		cursor_position = self.txtKnownLetters.cursorPosition()
		# Convert all text to uppercase automatically.
		self.txtKnownLetters.blockSignals(True)
		self.txtKnownLetters.setText(string.upper())
		self.txtKnownLetters.blockSignals(False)
		# Restore cursor position.
		self.txtKnownLetters.setCursorPosition(cursor_position)
		# Update corresponding fields to match, provided the string length is within the bounds.
		numLetters = len(string)
		self.gpbWordLength.blockSignals(True)
		self.slrWordLength.blockSignals(True)
		if 3 <= numLetters <= 15:
			self.gpbWordLength.setChecked(True)
			self.slrWordLength.setValue(len(string))
			self.lblWordLength.setNum(len(string))
		else:
			self.gpbWordLength.setChecked(False)
		self.gpbWordLength.blockSignals(False)
		self.slrWordLength.blockSignals(False)

	def handleWordLengthChanged(self, length):
		""" Updates other fields in the form when the word length slider is moved. """

		self.txtKnownLetters.blockSignals(True)
		self.txtKnownLetters.setText((self.txtKnownLetters.text() + '?'*15)[:length])
		self.txtKnownLetters.blockSignals(False)

	def handleWordLengthToggled(self, checked):
		""" Updates other fields in the form when known letters checkbox is toggled. """

		if checked:
			self.handleWordLengthChanged(self.slrWordLength.value())
		else:
			self.txtKnownLetters.blockSignals(True)
			self.txtKnownLetters.setText('')
			self.txtKnownLetters.blockSignals(False)


def scrollFix(self, event):
		"""
		An (unfortunately necessary) workaround to correct mouse scrolling behaviour in list boxes that have large items.
		By default it scrolls 3 rows at a time. Since these are large items, scrolling one at a time is preferred.
		This is a hacky override, but regrettably it is the only way. :(
		"""

		vb = self.verticalScrollBar()
		vb.setValue(vb.value()-np.sign(event.delta())) # apply desired scroll.

def run():
	""" Runs the program! """

	app = QtGui.QApplication(sys.argv)
	app.setWindowIcon(QtGui.QIcon('GUI/CCS.ico'))
	_ = CCSMain()
	sys.exit(app.exec_())

if __name__ == '__main__':
	run()