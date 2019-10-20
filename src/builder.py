#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from pathlib import Path
from typing import List, Tuple, NoReturn, Mapping
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element, SubElement, tostring

from networkx import DiGraph, NetworkXNotImplemented
from networkx.algorithms.dag import is_directed_acyclic_graph
from networkx.readwrite.graphml import parse_graphml, generate_graphml

from type_aliases import Architecture, Problem
from timed import timed_callable

# FUNCTIONS ###########################################################################################################


@timed_callable("Generating architecture from the '.cfg' file...")
def import_arch(filepath: Path) -> Architecture:
	"""Create the processor architecture from the configuration file, then returns it.

	Parameters
	----------
	filepath : Path
		A `Path` poiting to a *.cfg* file describing the processor architecture.

	Returns
	-------
	Architecture
		A list, each entry being a CPU, containing lists of integers,
		each integer being the `MacroTick` of a core.
		Basically we have : MacroTick = Architecture[cpu[core]].
	"""

	return [[
		core.get("MacroTick") for core in sorted(corelist, key=lambda e: e.get("Id"))
	] for corelist in [
		cpu for cpu in sorted(et.parse(filepath).findall("Cpu"), key=lambda e: e.get("Id"))
	]]


def insert_node_keys(graphml: Element, attributes: Mapping[str, str]) -> NoReturn:
	"""Add the <key> tags to a <graphml> tag from a dict of <node> attributes.

	Parameters
	----------
	graphml : Element
		A <graphml> root tag.
	attributes : Mapping[str, str]
		A dict of attributes to insert into `graphml` as <key> tags.
	"""

	for attribute, value in attributes.items():
		if attribute != "Id":

			key = SubElement(graphml, "key", {
				"id": "d" + str(len(graphml)),
				"for": "node",
				"attr.name": attribute.lower(),
				"attr.type": "string" if attribute == "Name" else "int"
			})

			if attribute != "Name":
				default = SubElement(key, "default")
				default.text = "-1" if attribute == "MaxJitter" or attribute == "CoreId" else "0"


def insert_chain_keys(graphml: Element, attributes: Mapping[str, str]) -> NoReturn:
	"""Add the <key> tags to a <graph> from a dict of <chain> attributes.

	Parameters
	----------
	graphml : Element
		A <graphml> root tag.
	attributes : Mapping[str, str]
		A dict of attributes to insert into `graphml` as <key> tags.
	"""

	for attribute, value in attributes.items():
		key = SubElement(graphml, "key", {
			"id": "d" + str(len(graphml)),
			"for": "graph",
			"attr.name": attribute.lower(),
			"attr.type": "string" if attribute == "Name" else "int"
		})

		if attribute != "Name":
			default = SubElement(key, "default")
			default.text = "0"


@timed_callable("Generating graph from  the '.tsk' file...")
def import_graph(filepath: Path) -> List[str]:
	"""Imports data from the given file and converts it into GraphML graphs, then returns it.
	One graph will be generated for each <Chain>.

	Parameters
	----------
	filepath : Path
		A `Path` to a *.tsk* file describing the task graph.

	Returns
	-------
	List[str]
		A list of `str` each containing a GraphML graph parsed from the <Chain> tags.
	"""

	graph_tree = et.parse(filepath)
	graph_list = list()

	# Add <graph> tags and their children <data>, <node> and <edge>
	for chain in graph_tree.iter("Chain"):
		# Add <graphml> document root
		graph_list.append(Element("graphml", {
			"xmlns": "http://graphml.graphdrawing.org/xmlns",
			"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
			"xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.1/graphml.xsd"
		}))

		# Add keys # TODO: transform into static elements
		insert_chain_keys(graph_list[-1], graph_tree.find("Graph/Chain").attrib)
		insert_node_keys(graph_list[-1], graph_tree.find("Graph/Node").attrib)

		# Add <graph> tag
		graph = SubElement(graph_list[-1], "graph", {
			"id": chain.get("Name"),
			"edgedefault": "directed"
		})

		# Add <data> tags for <graph> tag
		for key, value in chain.attrib.items():
			data = SubElement(
				graph,
				"data",
				{"key": graph_list[-1].findall("key[@attr.name='" + key.lower() + "']")[0].get("id")}
			)
			data.text = value

		# Add <node> tags for <graph> tag
		for i, runnable in enumerate(chain.iter("Runnable")):
			node = SubElement(graph, "node", {"id": str(len(graph.findall("node")))})

			# Add <data> tags for <node> tag
			for key, value in graph_tree.findall("Graph/Node[@Name='" + runnable.get("Name") + "']")[0].attrib.items():
				if key != "Id":
					data = SubElement(
						node,
						"data",
						{"key": graph_list[-1].findall("key[@attr.name='" + key.lower() + "']")[0].get("id")}
					)
					data.text = value

			# Add <edge> tag the <node> tag and its direct predecessor
			if i != 0:
				graph.append(Element("edge", {
					"source": graph.findall("node")[i - 1].get("id"),
					"target": node.get("id")
				}))

	return [tostring(graph) for graph in graph_list]


@timed_callable("Gathering the required files...")
def import_files_from_folder(folder_path: Path) -> Tuple[Path, Path]:
	"""Attempts to gather the required files in `folder_path`.

	Parameters
	----------
	folder_path : Path
		A `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.

	Returns
	-------
	Tuple[Path, Path]
		A pair of filepaths pointing to the `*.tsk` and `*.cfg` files.

	Raises
	------
	FileNotFoundError
		If no `*.tsk` or `*.cfg` file can be found.
	"""

	tsk = [element for element in folder_path.glob('*.tsk') if element.is_file()][0]
	cfg = [element for element in folder_path.glob('*.cfg') if element.is_file()][0]

	if tsk is None or cfg is None:
		raise FileNotFoundError("The folder " + folder_path.name + " include at least one *.tsk file and one *.cfg file.")

	if tsk.stem != cfg.stem:
		logging.warning("The names of the files mismatch: '" + tsk.stem + "' and '" + cfg.stem + "'")

	return (tsk, cfg)


def problem_builder(folder_path: Path) -> Problem:
	"""Creates a representation of the problem from the files in `folder_path`, and returns it.

	Parameters
	----------
	folder_path : Path
		A `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.

	Returns
	-------
	Problem
		A pair containing a `DiGraph` and an `Architecture` build from the files.

	Raises
	------
	NetworkXNotImplemented
		If one of the graphs contains a cycle.
	"""

	filepath_pair = import_files_from_folder(folder_path)
	logging.info("Files found:\n\t" + filepath_pair[0].name + "\n\t" + filepath_pair[1].name)

	graph_list = [DiGraph(parse_graphml(graph)) for graph in import_graph(filepath_pair[0])]
	for graph in graph_list:
		if not is_directed_acyclic_graph(graph):
			raise NetworkXNotImplemented("The graphs must be acyclic.")
	logging.info("Imported graphs:\n" + '\n'.join(['\n'.join(generate_graphml(graph)) for graph in graph_list]))

	architecture = import_arch(filepath_pair[1])
	logging.info("Imported architecture:\n\t" + '\n\t'.join(','.join(cpu) for cpu in architecture))

	return Problem(graphs=graph_list, arch=architecture)
