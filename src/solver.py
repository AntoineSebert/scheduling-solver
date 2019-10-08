#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from networkx import DiGraph
from typing import *
from logging import Logger

def is_equitable(graph: DiGraph, arch: List[int]) -> bool:
	"""Test whether an equitable coloration of the graph is possible or not.

	Parameters
	----------
	graph : DiGraph
		The directed oriented graph imported from the *.tsk* file.
	arch : List[int]
		The processor architecture imported from the *.cfg* file.

	Returns
	-------
	bool
		Returns `True` if an equitable coloration is possible, and `False` otherwise.
	"""

	return max([graph.degree(node) for node in graph.nodes]) <= sum(arch)

def generate_colorations(graph: DiGraph, arch: List[int]) -> Dict[str, Dict[object, int]]:
	"""Generate a graph coloration with an equitable strategy if possible, or potential graph colorations with greedy strategies.

	Parameters
	----------
	graph : DiGraph
		The directed oriented graph imported from the *.tsk* file.
	arch : List[int]
		The processor architecture imported from the *.cfg* file.

	Returns
	-------
	Dict[Dict[object, int]]
		A dictionary containing pairs of strategy names and possible graph colorations, each coloration being a dictionary containing pairs of nodes and colors.
	"""

	if is_equitable(graph, arch):
		return [equitable_color(graph, sum(arch))]
	else:
		"""Dictionary holding strategy names as keys and support for interchange as a boolean value."""
		strategies = {
			'largest_first': True,
			'random_sequential': True,
			#'smallest_last': True, # unstable for some reason
			'independent_set': False,
			'DSATUR': False
		}

		for strategy_name, interchange in strategies.items():
			coloration = greedy_color(graph, strategy_name, interchange)
			if 0 < len(coloration):
				processes_by_core = {}
				for key, value in sorted(greedy_color(graph, strategy_name, interchange).items()):
					processes_by_core.setdefault(value, []).append(key)

				strategies[strategy_name] = processes_by_core
			else:
				strategies.remove(strategy_name)

		return strategies

def validate_colorations(graph: DiGraph, colorations: Dict[str, Dict[object, int]]) -> Dict[str, Dict[object, int]]:
	"""Return a list of colorations expurged from the non-schedulable colorations.

	Parameters
	----------
	graph : DiGraph
		The directed oriented graph imported from the *.tsk* file.
	colorations : Dict[str, Dict[object, int]]
		The colorations list to validate.

	Returns
	-------
	Dict[str, Dict[object, int]]
		A dictionary containing pairs of strings and schedulable graph colorations.
	"""

	valid_colorations = dict()

	for strategy_name, coloration in colorations.items():
		for core, process_list in coloration.items():
			if not is_schedulable([graph.nodes(data=True)[process] for process in process_list]):
				valid_colorations.update({strategy_name: coloration})

	return valid_colorations

def color_graph(graph: DiGraph, coloration: Dict[object, int]):
	"""Color a graph using the given coloration.

	Parameters
	----------
	graph : DiGraph
		The directed oriented graph to color.
	coloration : Dict[object, int]
		The coloration to be applied to the graph.
	"""

	for node in coloration:
		graph.nodes[node]['color'] = coloration[node]

def scheduler(graph: DiGraph):
	# generate schedulable colorations
	print("Generating schedulable colorations...")
	colorations = validate_colorations(graph, generate_colorations(graph, arch))
	if len(colorations) == 0:
		print("No possible coloration. Terminating...")
		return -1
	print("Colorations found: ")
	for strategy_name, coloration in colorations.items():
		print("\t", strategy_name, ":", coloration)

	# color graph
	print("Coloring graph...")
	"""
	for node in coloration:
		G.nodes[node]['color'] = coloration[node]
	"""

	# display
	"""
	nx.draw_planar(G)
	plt.show()
	draw_console(G)
	"""

	# validate it
	print("Validating the solution...")
	# for each cpu for each core if is_schedulable() == False: raise NotSchedulable
	# check if https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.dag_longest_path.html shorter than deadline

	# draw it
	# https://networkx.github.io/documentation/stable/reference/drawing.html#module-networkx.drawing.nx_pylab

	print("Finished")