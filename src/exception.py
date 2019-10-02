# -*- coding: utf-8 -*-

class NoProcessor(Exception):
	"""Exception raised for errors in the input.

	Attributes
	----------
	message : str
		The explanation of the error.
	"""

	def __init__(self, message: str):
		self.message = message