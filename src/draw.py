#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import networkx
from networkx import DiGraph

# FUNCTIONS ###########################################################################################################


	"""Prints all nodes, including their attributes, and all edges, in the console.

	Parameters
	----------
	graph : DiGraph
		The directed graph to print.
	"""

	print("Printing graph content:")
	for node in graph.nodes(data=True):
		print("\t", node)
	for line in networkx.generate_edgelist(graph):
		print("\t", line)
