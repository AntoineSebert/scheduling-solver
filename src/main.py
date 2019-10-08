#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module aims to solve task scheduling problems.

Usage:
	main.py
	main.py --task <TASK> --conf <CONF>
	main.py --verbose
	main.py --task <TASK> --conf <CONF> --verbose
	main.py --benchmark
	main.py --task <TASK> --conf <CONF> --benchmark
	main.py (-h | --help)
	main.py --version

Options:
	-h --help		Show this screen.
	--version		Show version.
	--verbose		Toggle verbose output.
	--benchmark		Benchmark the greedy coloration strategies.
	--task <TASK>	The graph data in GraphML format [default: "data/case_1.tsk"].
	--conf <CONF>	The architecture data in XML [default: "data/case_1.cfg"].
"""

"""
Resources
- https://algorithm-visualizer.org/greedy/job-scheduling-problem
- https://visualgo.net/en/graphds
- https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019
- https://numpydoc.readthedocs.io/en/latest/format.html

Design patterns
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chain_of_responsibility__py3.py
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chaining_method.py

Static analysis
	tests
		https://github.com/pytest-dev/pytest
	type checking
		https://github.com/python/mypy
	style & quality
		https://gitlab.com/pycqa/flake8
	lint
		https://github.com/psf/black
Runtime analysis
	https://github.com/nedbat/coveragepy
	https://github.com/agermanidis/livepython
	https://github.com/benfred/py-spy
"""

# IMPORTS #############################################################################################################

import argparse
from io import TextIOWrapper
import matplotlib.pyplot as plt
import xml.etree.cElementTree as et

import networkx as nx
from networkx import DiGraph, HasACycle, NetworkXPointlessConcept, NetworkXNoCycle
from networkx.algorithms.cycles import find_cycle
from networkx.algorithms.coloring import *
from networkx.classes.function import is_empty
from networkx.readwrite.graphml import read_graphml

from rate_monotonic import *
from exception import *
from draw import *

# FUNCTIONS ###########################################################################################################

# I/O functions

def get_input_files() -> (TextIOWrapper, TextIOWrapper):
	"""Get the filepath for the *.tsk* and *.cfg* files from the CLI.

	Returns
	-------
	File_pair
		The pair of files to import as `TextIOWrapper`.
	"""

	parser = argparse.ArgumentParser(prog='SOLVER', description='Solve scheduling problems using graph coloration.', allow_abbrev=True)
	parser.add_argument(
		"--task",
		type = argparse.FileType('r', encoding="utf-8"),
		default = "data/case_1.tsk",
		help = "Import problem description from TASK file"
	)
	parser.add_argument(
		"--conf",
		type = argparse.FileType('r', encoding="utf-8"),
		default = "data/case_1.cfg",
		help = "Import system configuration from CONFIGURATION file"
	)
	parser.add_argument('--version', action='version', version='%(prog)s 0.0.1')
	args = parser.parse_args()

	return (args.task, args.conf)

def get_arch(filepath: TextIOWrapper) -> List[int]:
	"""Create the processor architecture from the configuration.

	Parameters
	----------
	filepath : TextIOWrapper
		The filepath to the *.cfg* file describing the processor architecture.

	Returns
	-------
	Architecture
		A list of integers, each entry being a cpu, and each integer being the number of cores.
	"""

	return [len(list(el)) for el in et.fromstring(filepath.read(-1)).findall('cpu')]

# Graph functions

def validate(graph: DiGraph):
	"""Validate the graph given as parameter. Especially checks if it is empty or contains cycles.

	Parameters
	----------
	graph : DiGraph
		The directed oriented graph imported from the *.tsk* file.

	Raises
	------
	NetworkXPointlessConcept
		If the graph is null.
	HasACycle
		If the graph contains at least a cycle.
	"""

	if is_empty(graph):
		raise NetworkXPointlessConcept("The provided graph cannot be empty.")

	try:
		find_cycle(graph)
	except NetworkXNoCycle as e:
		pass
	else:
		raise HasACycle("The provided directed graph must be acyclic.")

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


# ENTRY POINT #########################################################################################################

def main():
	"""Script entry point"""

	# import files
	print("Importing files...")
	file_pair = get_input_files()
	print("Files imported: ")
	print("\t" + file_pair[0].name)
	print("\t" + file_pair[1].name)

	# create graph
	print("Generating graph from  the '.tsk' file...")
	G = read_graphml(file_pair[0].name) # add custom named tuples
	print("Validating the graph...")
	validate(G)

	# display
	draw_console(G)
	"""
	pos = nx.layout.spring_layout(G)
	nx.draw_networkx(G, pos)
	plt.show()
	"""

	# get machine architecture
	print("Generating architecture from the '.cfg' file...")
	arch = get_arch(file_pair[1])

	# test if architecture is valid
	if len(arch) == 0:
		raise NoProcessor("The configuration must include at least one processor.")

	# display
	print("Number of cores and processors: ")
	print(*arch, sep='\n')

	# color graph
	print("Coloring graph...")
	strategies = {
		'largest_first': True,
		'random_sequential': True,
		'smallest_last': True,
		'independent_set': False,
		'DSATUR': False
	}
	if max([G.degree(node) for node in G.nodes]) <= sum(arch):
		equitable_color(G, sum(arch))
	else:
		greedy_color(G, 'saturation_largest_first')

	# display
	"""
	nx.draw_planar(G)
	plt.show()
	"""
	draw_console(G)

	# solve it
	print("Solving the scheduling problem...")
	# ...

	# validate it
	print("Validating the solution...")
	# for each cpu for each core if is_schedulable() == False: raise NotSchedulable
	# check if https://networkx.github.io/documentation/stable/reference/algorithms/generated/networkx.algorithms.dag.dag_longest_path.html shorter than deadline

	# draw it
	# https://networkx.github.io/documentation/stable/reference/drawing.html#module-networkx.drawing.nx_pylab

	# simulate
	print("Launching the simulation...")
	# https://github.com/dbader/schedule

	print("Finished")

if __name__ == "__main__":
	main()