#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from enum import Enum, unique
from functools import partial
from json import dumps
from pathlib import Path
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, fromstringlist, tostring

from datatypes import PriorityQueueEncoder, Solution

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
			schedule.extend([
				Element("Slice", {
					"TaskId": str(_slice.task_id), "Start": str(_slice.start), "Duration": str(_slice.end - _slice.start)
				}) for _slice in core.slices
			])

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

	title = "Solution for " + (
		str(solution.filepaths.tsk.parts[-2]) if 0 < len(solution.filepaths.tsk.parts) else str(Path.cwd())
	)

	svg = fromstringlist([
		"<?xml version='1.0' ?>",
		"<svg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' width='100%' height='100%' lang='en' version='1.1'>",
			f"<title>{title}</title>",  # noqa: E131
			"<desc>An horizontal chart bar showing the solution to the scheduling problem.</desc>",
			"<style>",  # https://www.w3.org/TR/SVG2/styling.html
			"</style>",
			"<defs>",
				"<symbol id='cpu' class='cpu'>",  # noqa: E131
					"<text>CPU</text>",  # noqa: E131
					"<g class='cores'></g>",
				"</symbol>",
				"<symbol id='core' class='core'>",
					"<text>CORE</text>",
					"<g class='slices'></g>",
					"<path y1='0' x1='0' y2='10' x2='10' />",
					"<marker></marker>",  # <circle cx="6" cy="6" r="3" fill="white" stroke="context-stroke" stroke-width="2"/>
				"</symbol>",
				"<symbol id='slice' class='slice'>",
					"<text>SLICE</text>",
					"<text>start</text>",
					"<text>end</text>",
					"<rect x='100' y='100' width='400' height='200' rx='50' fill='green' />",
				"</symbol>",
				"<linearGradient id='background' y2='100%'>",
					"<stop offset='5%' stop-color='rgba(3,126,243,1)' />",
					"<stop offset='95%' stop-color='rgba(48,195,158,1)' />",
				"</linearGradient>",
			"</defs>",
			"<rect fill='url(#background)' x='0' y='0' width='100%' height='100%' />",
			f"<text x='30%' y='10%'>{title}</text>",
			"<g>",
				"".join(f"<use id='cpu_{cpu.id}' xlink:href='#cpu' x='5%' y='{i * (15 * len(cpu.cores))}'>" + str(cpu.id) + "</use>" for i, cpu in enumerate(solution.arch)),
			"</g>",
		"</svg>"
	])

	for cpu in solution.arch:
		Element("use", {"id": str(cpu.id)})
		for core in cpu.cores:
			Element("use", {"id": str(core.id)})

	return tostring(svg)


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
