# -*- coding: utf-8 -*-

import networkx as nx

def draw_console(G: nx.DiGraph):
	"""Prints all nodes, including their attributes, and all edges."""

	print("Printing graph content:")
	for node in G.nodes(data=True):
		print("\t", node)
	for line in nx.generate_edgelist(G):
		print("\t", line)