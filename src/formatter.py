#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from enum import Enum, unique
from functools import partial
from typing import Iterable, List
from xml.etree.ElementTree import ElementTree, SubElement, tostring, Element
from xml.dom.minidom import parseString
import json

from datatypes import Solution
from timed import timed_callable


# FUNCTIONS ###########################################################################################################


@timed_callable("Formatting the solutions to JSON...")
def _json_format(solutions: Iterable[Solution]) -> List[str]:
	"""Formats an iterable of `Solution` into JSON.

	Parameters
	----------
	solutions : Iterable[Solution]
		An iterable of `Solution`.

	Returns
	-------
	List[str]
		A list of `str`, each representing a `Solution`.
	"""

	raise NotImplementedError()


@timed_callable("Formatting the solutions to XML...")
def _xml_format(solutions: Iterable[Solution]) -> List[str]:
	"""Formats an iterable of `Solution` into a custom XML schema.

	Parameters
	----------
	solutions : Iterable[Solution]
		An iterable of `Solution`.

	Returns
	-------
	List[str]
		A list of `str`, each representing a `Solution`.
	"""

	formatted = list()

	for solution in solutions:
		tables = Element("Tables")
		for key, val in solution.items():
			for i, tasklist in enumerate(val):
				schedule = SubElement(tables, "Schedule", {"CpuId": str(key), "CoreId": str(i)})
				schedule.extend(
					[Element("Slice", {
						"TaskId": _slice.task,
						"Start": str(_slice.start),
						"Duration": str(_slice.end - _slice.start)
					}) for _slice in tasklist]
				)
		formatted.append(parseString(tostring(tables)).toprettyxml())

	return formatted


@timed_callable("Formatting the solutions to GRAPHML...")
def _graphml_format(solutions: Iterable[Solution]) -> List[str]:
	"""Formats an iterable of `Solution` into GraphML.

	Parameters
	----------
	solutions : Iterable[Solution]
		An iterable of `Solution`.

	Returns
	-------
	List[str]
		A list of `str`, each representing a `Solution`.
	"""

	raise NotImplementedError()


@timed_callable("Formatting the solutions to JSON...")
def _raw_format(solutions: Iterable[Solution]) -> List[str]:
	"""Formats an iterable of `Solution` into a list of `str`.

	Parameters
	----------
	solutions : Iterable[Solution]
		An iterable of `Solution`.

	Returns
	-------
	List[str]
		A list of `str`, each representing a `Solution`.
	"""

	return [str(solution) for solution in solutions]


# CLASSES #############################################################################################################

@unique
class OutputFormat(Enum):
	"""...

	Parameters
	----------
	solutions : Iterable[Solution]
		...

	Returns
	-------
	List[str]
		...
	"""

	xml = partial(_xml_format)
	json = partial(_json_format)
	graphml = partial(_graphml_format)
	raw = partial(_raw_format)

	def __call__(self, solutions: Iterable[Solution]) -> str:
		return self.value(solutions)
