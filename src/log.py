#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from logging import Handler
from typing import NoReturn

# CLASSES #############################################################################################################

class Singleton(type):
	"""A Singleton class, meant to be extended.

	Attributes
	----------
	_instances : Dict[__class__, Singleton]
		Holds classes as keys and single class instances of all subclasses as values.

	Methods
	-------
	emit(cls, *args, **kwargs)
		Creates the instance if it does not yet exists and returns it.
	"""

	# Holds classes as keys and single class instances of all subclasses as values.
	_instances = {}

	def __call__(cls, *args, **kwargs):
		"""Called when the instance is "called" as a function; if this method is defined, `x(arg1, arg2, ...)` is a shorthand for `x.__call__(arg1, arg2, ...)`.

		Parameters
		----------
		cls : __class__
			The caller class.
		args : Tuple[object]
			A tuple of positional arguments values (default is empty tuple).
		kwargs : Dict[str, object]
			A dict of keyword arguments values (default is empty dict).

		Returns
		-------
		Singleton
			The single instance of the caller class.
		"""

		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class colored_handler(Handler, metaclass=Singleton):
	"""Configures the logger.

	Attributes
	----------
	_colors : Dict[int, str]
		Holds logging level names as keys and colors as values.
		(default is { logging.CRITICAL: '\033[91m', logging.ERROR: '\033[91m', logging.WARNING: '\033[93m', logging.INFO: '\033[94m', logging.DEBUG: '\033[92m', })
	_styles : Dict[int, str]
		Holds strings representing styles as keys and styles as values.
		(default is { "bold": '\033[1m', "italic": '\033[3m', "underline": '\033[4m', })
	_reset : str
		Reset color and style formatting (default is '\033[0m').
	_verbose : bool
		Verbose mode (default is False).
	_formatters : Dict[int, logging.Formatter]
		Holds logging level values as keys and `Formatter` as values (default is dict()).

	Methods
	-------
	emit(record)
		Formats and prints a `LoggerRecord` parameter, depending on the verbosity level.
	"""

	# Holds logging level names as keys and colors as values.
	_colors = {
		logging.CRITICAL:	'\033[91m',
		logging.ERROR:		'\033[91m',
		logging.WARNING:	'\033[93m',
		logging.INFO:		'\033[94m',
		logging.DEBUG:		'\033[92m',
	}
	# Holds strings representing styles as keys and styles as values.
	_styles = {
		"bold":			'\033[1m',
		"italic":		'\033[3m',
		"underline":	'\033[4m',
	}
	# Reset color and style formatting.
	_reset =	'\033[0m'
	# Verbosity.
	_verbose = False
	# Holds logging level values as keys and `Formatter` as values.
	_formatters = dict()

	def __init__(self, verbose: bool):
		"""Called after the instance has been created (by `__new__()`), but before it is returned to the caller.
		The arguments are those passed to the class constructor expression.
		If a base class has an `__init__()` method, the derived class’s `__init__()` method, if any, must explicitly call it to ensure proper initialization of the base class part of the instance; for example: `super().__init__([args...])`.

		Parameters
		----------
		verbose : bool
			Toggle the verbosity.

		Returns
		-------
		colored_handler
			The single instance of the class.
		"""

		Handler.__init__(self)
		logging.getLogger().setLevel(0)
		self._verbose = verbose

		for key, value in self._colors.items():
			self._formatters[key] = logging.Formatter(fmt=value+'[%(asctime)s][%(levelname)s]: %(message)s'+self._reset, datefmt='%H:%M:%S')

	def emit(self, record) -> NoReturn:
		"""Formats and prints a `LoggerRecord` parameter, depending on the verbosity.

		Parameters
		----------
		verbosity : bool
			Verbosity. If set to `False`, log levels under `ERROR` are not printed.

		"""
		if self._verbose or 30 < record.levelno:
			print(self._formatters[record.levelno].format(record))