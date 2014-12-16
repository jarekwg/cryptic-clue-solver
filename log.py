# -*- coding: utf-8 -*-

"""
A custom logging wrapper; writes to both file and console.
"""

import logging
from logging.handlers import RotatingFileHandler

# Re-define these, so that they're accessible to other modules that import this module
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def getLogger(name, streamLevel=logging.WARNING, fileLevel=logging.DEBUG):

	# Create the new logger.
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	# Add handlers (if not already added).
	if not logger.handlers:
		# Setup formatting.
		formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

		# Setup stdout logging.
		handler = logging.StreamHandler()
		handler.setLevel(streamLevel)
		handler.setFormatter(formatter)
		logger.addHandler(handler)

		# Setup file logging (for last run only).
		handler = logging.FileHandler('CCS_lastRun.log', 'w+')
		handler.setLevel(fileLevel)
		handler.setFormatter(formatter)
		logger.addHandler(handler)

		# Setup file logging (cumulative).
		handler = logging.FileHandler('CCS.log', 'a+')
		handler.setLevel(logging.WARNING) # limit this one to warnings only, else things get out of hand very quickly
		handler.setFormatter(formatter)
		logger.addHandler(handler)


	return logger