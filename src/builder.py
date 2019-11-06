#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


import logging
from pathlib import Path
import xml.etree.ElementTree as et

from ortools.sat.python.cp_model import CpModel

from datatypes import Architecture, Problem, Processor, Core, Node, Graph, Filepaths
from timed import timed_callable


# FUNCTIONS ###########################################################################################################


def _import_arch(filepath: Path) -> Architecture:
	"""Create the processor architecture from the configuration file, then returns it.

	Parameters
	----------
	filepath : Path
		A `Path` to a *.cfg* file describing the processor architecture.

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
			) for core in sorted(cpu, key=lambda e: int(e.get("Id")))
		]) for cpu in sorted(et.parse(filepath).iter("Cpu"), key=lambda e: int(e.get("Id")))
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
		An iterable of `Node`.
	"""

	return [
		Node(
			i,
			node.get("Name"),
			int(node.get("WCET")),
			int(node.get("Period")),
			int(node.get("Deadline")),
			int(node.get("MaxJitter")) if int(node.get("MaxJitter")) != -1 else None,
			int(node.get("Offset")),
			int(node.get("CpuId")),
			int(node.get("CoreId")) if int(node.get("CoreId")) != -1 else None
		) for i, node in enumerate(sorted(et.parse(filepath).iter("Node"), key=lambda e: int(e.get("Id"))))
	]


# ENTRY POINT #########################################################################################################


@timed_callable("Building the problem...")
def build(filepath_pair: Filepaths) -> Problem:
	"""Creates an internal representation for a problem.

	Parameters
	----------
	filepath_pair : Filepaths
		A `Filepaths` pointing to the `*.tsk` and `*.cfg` files.

	Returns
	-------
	Problem
		A `Problem` generated from the test case.
	"""

	graph = _import_graph(filepath_pair.tsk)
	logging.info("Imported graphs from " + filepath_pair.tsk.name)

	arch = _import_arch(filepath_pair.cfg)
	logging.info("Imported architecture from " + filepath_pair.cfg.name)

	return Problem(filepath_pair, graph, arch)
