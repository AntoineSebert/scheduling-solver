#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from enum import Enum, unique
from functools import partial
from xml.etree.ElementTree import SubElement, tostring, Element
from xml.dom.minidom import parseString
from json import dumps

from datatypes import Solution, PriorityQueueEncoder
from timed import timed_callable


# FUNCTIONS ###########################################################################################################


@timed_callable("Formatting the solutions to JSON...")
def _json_format(solution: Solution) -> str:
	"""Formats a solution into JSON.

	Parameters
	----------
	solution : Solution
		A `Solution`.

	Returns
	-------
	str
		A `str` representing a JSON `Solution`.
	"""

	return dumps(solution, skipkeys=True, sort_keys=True, indent=4, cls=PriorityQueueEncoder)


@timed_callable("Formatting the solutions to XML...")
def _xml_format(solution: Solution) -> str:
	"""Formats a solution into a custom XML schema.

	Parameters
	----------
	solution : Solution
		A `Solution`.

	Returns
	-------
	str
		A `str` representing a XML `Solution`.
	"""

	tables = Element("Tables")
	for cpu in solution.arch:
		for core in cpu.cores:
			schedule = SubElement(tables, "Schedule", {"CpuId": str(cpu.id), "CoreId": str(core.id)})
			schedule.extend(
				Element("Slice", {
					"TaskId": slice.task, "Start": str(slice.start), "Duration": str(slice.end - slice.start)
				}) for slice in core.slices
			)

	return parseString(tostring(tables)).toprettyxml()


@timed_callable("Formatting the solution to a raw string representation...")
def _raw_format(solution: Solution) -> str:
	"""Formats a solution into string.

	Parameters
	----------
	solution : Solution
		A `Solution`.

	Returns
	-------
	str
		A `str` representing a `Solution` object.
	"""

	return str(solution)


@timed_callable("Formatting the solution to SVG...")
def _svg_format(solution: Solution) -> str:
	"""Formats a solution into SVG.

	Parameters
	----------
	solution : Solution
		A `Solution`.

	Returns
	-------
	str
		A `str` representing a SVG `Solution`.
	"""

	# stuff

	return str(solution)


# CLASSES #############################################################################################################

@unique
class OutputFormat(Enum):
	"""An enumeratino those purpose it to map format keywords to formatting functions.

	Attributes
	----------
	xml : partial
		Callable object mapped to a XML formatter (custom module format).
	json : partial
		Callable object mapped to a JSON formatter.
	raw : partial
		Callable object mapped to a raw formatter (`solution` is converted into a `str`).
	svg : partial
		Callable object mapped to the raw formatter (`solution` is converted into a `str`).

	Methods
	-------
	__call__
		Converts the enumeration member into the corresponding function call.
	"""

	xml: partial = partial(_xml_format)
	json: partial = partial(_json_format)
	raw: partial = partial(_raw_format)
	svg: partial = partial(_svg_format)

	def __call__(self, solution: Solution) -> str:
		"""Converts the enumeratino member into the corresponding function call.

		Parameters
		----------
		solution : Solution
			An `Solution`.

		Returns
		-------
		str
			A `str` representing a `Solution`.
		"""

		return self.value(solution)
