# -*- coding: utf-8 -*-

"""This module aims to solve task scheduling problems."""

"""
Resources
- https://algorithm-visualizer.org/greedy/job-scheduling-problem
- https://visualgo.net/en/graphds
- https://docs.microsoft.com/en-us/visualstudio/python/working-with-c-cpp-python-in-visual-studio?view=vs-2019
- https://numpydoc.readthedocs.io/en/latest/format.html

Data structure : acyclic directed weighted graph

Design patterns
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/strategy.py
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chain_of_responsibility__py3.py
- https://github.com/faif/python-patterns/blob/master/patterns/behavioral/chaining_method.py

Analysis
- https://github.com/nedbat/coveragepy
- https://github.com/facebook/pyre-check
- https://github.com/python/mypy
- https://gitlab.com/pycqa/flake8
"""

"""
time benchmark
logging : https://docs.python.org/3/library/logging.html
progressbar
benchmark strats
random problem generation : https://networkx.github.io/documentation/stable/reference/randomness.html
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

def get_input_files() -> (TextIOWrapper, TextIOWrapper):
	"""Get the filepath for the *.tsk* and *.cfg* files from the CLI.

	Returns
	-------
	File_pair
		The pair of files to import as `TextIOWrapper`.
	"""

	parser = argparse.ArgumentParser(prog='SOLVER', description='Solve scheduling problems.', allow_abbrev=True)
	parser.add_argument(
		"--task",
		nargs = '?',
		type = argparse.FileType('r', encoding="utf-8"),
		default = "data/case_1.tsk",
		help = "Import problem description from TASK file"
	)
	parser.add_argument(
		"--conf",
		nargs = '?',
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