#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import NoReturn, Iterable
from concurrent.futures import ThreadPoolExecutor

from networkx import DiGraph

import logging
from timed import timed_callable
from type_aliases import Architecture, Problem
from rate_monotonic import is_schedulable

# FUNCTIONS ###########################################################################################################


def chain_stress(graph: DiGraph) -> float:
	"""Computes the stress ratio for a graph.

	Parameters
	----------
	graph : DiGraph
		An oriented task graph.

	Returns
	-------
	float
		The stress level for the graph.

	Raises
	------
	NetworkXNotImplemented
		If the chain budget is shorter than the scheduled tasks duration.
	"""

	assigned_tasks_duration = sum([node[1]["wcet"] for node in graph.nodes(data=True) if node[1]["coreid"] != -1])

	if graph.graph["budget"] < assigned_tasks_duration:
		raise NotImplementedError("The Chain duration is shorter than the total tasks duration")

	return (graph.graph["budget"] - assigned_tasks_duration) / sum([node[1]["wcet"] for node in graph.nodes(data=True) if node[1]["coreid"] == -1])

@timed_callable("Generating a coloration for the problem...")
def color_graphs(problem: Problem) -> NoReturn:
	"""Color the graphs within the problem.

	Parameters
	----------
	problem : Problem
		The problem from which statement.
	"""

	valid_colorations = dict()

	for strategy_name, coloration in colorations.items():
		for core, process_list in coloration.items():
			if not is_schedulable([graph.nodes(data=True)[process] for process in process_list]):
				valid_colorations.update({strategy_name: coloration})

	return valid_colorations


	# for each no_processor(node) or no_core(node)
	# assign top queue to node (same processor)


		graph.nodes[node]['color'] = coloration[node]
def theoretical_scheduling_time(graph: DiGraph) -> int:
	"""Computes the theoretical scheduling time of a graph.

	Parameters
	----------
	graph : DiGraph
		An oriented task graph.

	Returns
	-------
	int
		The theoretical shortest scheduling time for `graph`.
	"""

	return sum([node[1]["wcet"] for node in graph.nodes(data=True)])


@timed_callable("Computing shortest theoretical scheduling time...")
def shortest_theoretical_scheduling(graphs: Iterable[DiGraph]) -> int:
	"""Computes the shortest theoretical scheduling time from the longest scheduling path of all graphs.

	Parameters
	----------
	graphs: Iterable[DiGraph]
		An iterable of directed oriented graph imported from the `Problem`.

	Returns
	-------
	int
		The theoretical shortest scheduling time.
	"""

	with ThreadPoolExecutor(max_workers=len(graphs)) as executor:
		futures = [executor.submit(theoretical_scheduling_time, graph) for graph in graphs]

	return min([future.result() for future in futures])


def scheduler(problem: Problem):
	"""Generates a solution for the problem.

	Parameters
	----------
	problem : Problem
		A `Problem` from the problem builder.

	Returns
	-------
	Optional[Solution]
		A solution if there is one, or `None` otherwise.
	"""

	logging.info(
		"Theoretical shortest scheduling time (in microseconds):\t" + str(shortest_theoretical_scheduling(problem[0]))
	)

	coloration = color_graphs(problem)

	"""
	logging.info(
		"Colorations found:\n\t" + '\n\t'.join(coloration for coloration in colorations)
	)
	"""
	"""
	nx.draw_planar(G)
	plt.show()
	draw_console(G)
	"""
	"""
	# validate it
	print("Validating the solution...")

	# draw it
	# https://networkx.github.io/documentation/stable/reference/drawing.html#module-networkx.drawing.nx_pylab
	"""
	return object
