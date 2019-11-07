#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from logging import Handler, LogRecord
from typing import Any, Dict, NoReturn

# CLASSES #############################################################################################################


class Singleton(type):
	"""A singleton, meant to be extended.

	Attributes
	----------
	_instances : Dict[Any, Singleton]
		Holds subclasses as keys and instances of said subclasses as values.

	Methods
	-------
	__call__(cls, *args, **kwargs)
		Creates the instance if it does not yet exists and returns it.
	"""

	_instances = {}

	def __call__(cls: Any, *args: Any, **kwargs: Dict[str, Any]) -> Any:
		"""Called when the instance is "called" as a function; if this method is defined, `x(arg1, arg2, ...)`
		is a shorthand for `x.__call__(arg1, arg2, ...)`.

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
		Any
			The single instance of the caller class.
		"""

		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

		return cls._instances[cls]


class ColoredHandler(Handler, metaclass=Singleton):
	"""Configures the logger.

	Attributes
	----------
	_colors : Dict[int, str]
		Holds logging level names as keys and colors as values.
		(default is { logging.CRITICAL: '\033[91m', logging.ERROR: '\033[91m', logging.WARNING: '\033[93m',
		logging.INFO: '\033[94m', logging.DEBUG: '\033[92m', })
	_styles : Dict[str, str]
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
	__init__(self, verbose: bool = False)
		Initializes the Handler.
	emit(record)
		Formats and prints a `LoggerRecord` parameter, depending on the verbosity level.
	"""

	_colors = {
		logging.CRITICAL: '\033[91m',
		logging.ERROR: '\033[91m',
		logging.WARNING: '\033[93m',
		logging.INFO: '\033[94m',
		logging.DEBUG: '\033[92m',
	}
	_styles = {
		"bold": '\033[1m',
		"italic": '\033[3m',
		"underline": '\033[4m',
	}
	_reset = '\033[0m'
	_verbose = False
	_formatters = {}

	def __init__(self: Singleton, verbose: bool = False) -> NoReturn:
		"""Called after the instance has been created (by `__new__()`), but before it is returned to the caller.
		The arguments are those passed to the class constructor expression.
		If a base class has an `__init__()` method, the derived class’s `__init__()` method, if any,
		must explicitly call it to ensure proper initialization of the base class part of the instance;
		for example: `super().__init__([args...])`.

		Parameters
		----------
		verbose : bool
			Toggle the verbosity (default: False).
		"""

		Handler.__init__(self)
		logging.getLogger().setLevel(0)
		__class__._verbose = verbose
		__class__._formatters = {key: logging.Formatter(
			fmt=value + '[%(asctime)s][%(levelname)s]: %(message)s' + __class__._reset,
			datefmt='%H:%M:%S',
		) for key, value in __class__._colors.items()}

	def emit(self: Singleton, record: LogRecord) -> NoReturn:
		"""Formats and prints a `LoggerRecord` parameter, depending on the verbosity.

		Parameters
		----------
		record : logging.LogRecord
			A record to format and print.
		"""

		if __class__._verbose or 30 < record.levelno:
			print(__class__._formatters[record.levelno].format(record))
