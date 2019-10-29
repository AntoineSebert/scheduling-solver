#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


import logging
from pathlib import Path
from typing import Tuple
import xml.etree.ElementTree as et

from datatypes import Architecture, Problem, Processor, Core, Node, Chain, Graph
from timed import timed_callable


# FUNCTIONS ###########################################################################################################


def _import_arch(filepath: Path) -> Architecture:
	"""Create the processor architecture from the configuration file, then returns it.

	Parameters
	----------
	filepath : Path
		A `Path` poiting to a *.cfg* file describing the processor architecture.

	Returns
	-------
	Architecture
		An iterable of `Processor`.
	"""

	return [
		Processor(int(cpu.get("Id")), (0.0, None), [
			Core(
				int(core.get("Id")),
				int(core.get("MacroTick")) if int(core.get("MacroTick")) != 9999999 else None,
				0.0,
				list()
			) for core in cpu
		]) for cpu in et.parse(filepath).findall("Cpu")
	]


def _import_graph(filepath: Path) -> Graph:
	"""Creates the graph from the tasks file, then returns it.

	Parameters
	----------
	filepath : Path
		A `Path` to a *.tsk* file describing the task graph.

	Returns
	-------
	Graph
		An iterable of chains.
	"""

	graph_tree = et.parse(filepath)

	graph = list()
	for chain in graph_tree.iter("Chain"):
		tasks = list()
		for task in chain:
			# get node attributes
			attrs = graph_tree.findall("Graph/Node[@Name='" + task.get("Name") + "']")[0].attrib
			# create node
			tasks.append(Node(
				len(tasks),
				task.get("Name"),
				int(attrs["WCET"]),
				int(attrs["Period"]),
				int(attrs["Deadline"]),
				int(attrs["MaxJitter"]) if int(attrs["MaxJitter"]) != -1 else None,
				int(attrs["Offset"]),
				int(attrs["CpuId"]),
				int(attrs["CoreId"]) if int(attrs["CoreId"]) != -1 else None,
			))
		graph.append(Chain(len(graph), int(chain.get("Budget")), int(chain.get("Priority")), tasks))

	return graph


# ENTRY POINT #########################################################################################################


@timed_callable("Building the problem...")
def build(filepath_pair: Tuple[Path, Path]) -> Problem:
	"""Creates an internal representation for a problem.

	Parameters
	----------
	filepath_pair : Tuple[Path, Path]
		A pair of filepaths pointing to the `*.tsk` and `*.cfg` files.

	Returns
	-------
	Problem
		A problem generated from the test case.
	"""

	graph = _import_graph(filepath_pair[0])
	logging.info("Imported graphs from " + filepath_pair[0].name)

	arch = _import_arch(filepath_pair[1])
	logging.info("Imported architecture from " + filepath_pair[1].name)

	return Problem(str(filepath_pair[0]), graph, arch)
