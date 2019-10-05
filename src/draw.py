# -*- coding: utf-8 -*-

import networkx as nx

def draw_console(graph: nx.DiGraph):
	"""Prints all nodes, including their attributes, and all edges, in the console.

	Parameters
	----------
	graph : DiGraph
		The directed graph to print.
	"""

	print("Printing graph content:")
	for node in graph.nodes(data=True):
		print("\t", node)
	for line in nx.generate_edgelist(graph):
		print("\t", line)