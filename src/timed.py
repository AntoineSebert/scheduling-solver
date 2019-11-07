#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Dict, Optional

import log


# FUNCTIONS ###########################################################################################################


def timed_callable(message: str) -> Optional[Any]:
	"""Logs the time taken by a `Callable` to run (in seconds), and returns its eventual return values.

	Parameters
	----------
	message : str
		The message to display before the running `Callable`.
	callable : Callable
		The `Callable` to run.
	args, kwds
		The arguments to pass to the `Callable`.

	Returns
	-------
	result : Opional[Any]
		The value eventually returned by the `Callable`.
	"""

	def callable_decorator(callable: Callable) -> Optional[Any]:
		@wraps(callable)
		def timed_wrapper(*args: Any, **kwds: Dict[str, Any]) -> Optional[Any]:
			result = None

			if 0 < len(message):
				logging.info(message)

				start = perf_counter()
				result = callable(*args, **kwds)
				end = perf_counter()

				logging.info("Done in " + str(end - start) + "s.")
			else:
				log.error("Cannot call timed callable" + str(callable) + ": there is no message.")

			return result
		return timed_wrapper

	return callable_decorator
