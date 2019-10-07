#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class NoProcessor(Exception):
	"""Exception raised when no processor is found in the configuration file.

	Attributes
	----------
	message : str
		The explanation of the error.
	"""

	def __init__(self, message: str):
		self.message = message