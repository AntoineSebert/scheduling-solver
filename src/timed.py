#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from typing import Any, Callable, Optional
from time import perf_counter
from functools import wraps

# FUNCTIONS ###########################################################################################################

def timed_callable(message: str) -> Optional[Any]:
	"""Logs the time taken by a `Callable` to run (in seconds), and returns its eventual return values.

	Parameters
	----------
	message : str
		The message to display before the running `Callable`.
	callable : Callable
		The `Callable` to run.
	args
		The arguments to pass to the `Callable`.

	Returns
	-------
	result : Opional[Any]
		The value eventually returned by the `Callable`.
	"""

	assert(0 < len(message))

	@wraps(callable)
	def callable_decorator(callable: Callable) -> Optional[Any]:
		def timed_wrapper(*args, **kwds) -> Optional[Any]:

			logging.info(message)
			start = perf_counter()
			result = callable(*args, **kwds) # if args != None and kwargs == None
			end = perf_counter()
			logging.info("Done in " + str(end - start) + "s.")

			return result
		return timed_wrapper
	return callable_decorator
