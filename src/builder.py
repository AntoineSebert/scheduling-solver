#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


import logging
from pathlib import Path

from datatypes import Architecture, Core, FilepathPair, Graph, Node, Problem, Processor

from defusedxml import ElementTree

from ortools.sat.python.cp_model import CpModel

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
		Processor(
			i,
			(0.0, None),
			[
				Core(
					ii,
					int(core.get("MacroTick")) if int(core.get("MacroTick")) != 9999999 else None,
					0.0,
					[],
				) for ii, core in enumerate(sorted(cpu, key=lambda e: int(e.get("Id"))))
			],
		) for i, cpu in enumerate(sorted(ElementTree.parse(filepath).iter("Cpu"), key=lambda e: int(e.get("Id"))))
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
			int(node.get("CoreId")) if int(node.get("CoreId")) != -1 else None,
		) for i, node in enumerate(sorted(ElementTree.parse(filepath).iter("Node"), key=lambda e: int(e.get("Id"))))
	]


# ENTRY POINT #########################################################################################################


@timed_callable("Building the problem...")
def build(filepath_pair: FilepathPair) -> Problem:
	"""Creates an internal representation for a problem.

	Parameters
	----------
	filepath_pair : FilepathPair
		A `FilepathPair` pointing to the `*.tsk` and `*.cfg` files.

	Returns
	-------
	Problem
		A `Problem` generated from the test case.
	"""

	graph = _import_graph(filepath_pair.tsk)
	logging.info("Imported graphs from " + filepath_pair.tsk.name)

	arch = _import_arch(filepath_pair.cfg)
	logging.info("Imported architecture from " + filepath_pair.cfg.name)

	model = CpModel()

	# CREATE VARIABLES
	"""
	num_vals = 3
	x = model.NewIntVar(0, num_vals - 1, 'x')
	y = model.NewIntVar(0, num_vals - 1, 'y')
	z = model.NewIntVar(0, num_vals - 1, 'z')
	"""

	# CREATE CONSTRAINTS : model.Add(x != y)

	# ADD OBJECTIVE FUNCTION : model.Maximize(x + 2 * y + 3 * z)

	return Problem(filepath_pair, graph, arch, model)
