#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import List, Tuple
from pathlib import Path
import xml.etree.ElementTree as et
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
import logging

import xml.dom.minidom

from networkx import DiGraph
from networkx.readwrite.graphml import parse_graphml
from networkx.algorithms.dag import is_directed_acyclic_graph, dag_longest_path

from type_aliases import Architecture
from timed import timed_callable

# FUNCTIONS ###########################################################################################################

@timed_callable("Generating architecture from the '.cfg' file...")
def import_arch(filepath: Path) -> Architecture:
	"""Create the processor architecture from the configuration file, then returns it.

	Parameters
	----------
	filepath : Path
		The `Path` to the *.cfg* file describing the processor architecture.

	Returns
	-------
	Architecture
		A `List`, each entry being a CPU, containing `List`s, each entry being a core, of integers, each integer being the `MacroTick` of the core.
		Basically we have : MacroTick = Architecture[cpu[core]].
	"""

	sorting = lambda e: e.get("Id")
	arch = [[core.get("MacroTick") for core in sorted(corelist, key=sorting)] for corelist in [cpu for cpu in sorted(et.parse(filepath).findall("Cpu"), key=sorting)]]

	logging.info("Imported architecture:\n" + '\n\t'.join(','.join(cpu) for cpu in arch))

	return arch

@timed_callable("Generating graph from  the '.tsk' file...")
def import_graph(filepath: Path) -> str:
	"""Imports data from the given file and converts it into GraphML, then returns it.

	Parameters
	----------
	filepath : Path
		The `Path` to the *.tsk* file describing the task graph.

	Returns
	-------
	str
		A `str` object containing a GraphML parsed from the file given as parameter.
	"""

	graph_tree = et.parse(filepath)

	graphml = Element("graphml", {
		"xmlns": "http://graphml.graphdrawing.org/xmlns",
		"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
		"xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.1/graphml.xsd"
	})

	# Add <key> elements for <node> tags.
	for attribute, value in graph_tree.find("Graph/Node").attrib.items():
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

	# Add <key> elements for <graph> tags
	for attribute, value in graph_tree.find("Graph/Chain").attrib.items():
		key = SubElement(graphml, "key", {
			"id": "d" + str(len(graphml)),
			"for": "graph",
			"attr.name": attribute.lower(),
			"attr.type": "string" if attribute == "Name" else "int"
		})

		if attribute != "Name":
			default = SubElement(key, "default")
			default.text = "0"

	# Add <graph> tags and their children <data>, <node> and <edge>
	for chain in graph_tree.iter("Chain"):
		graph = SubElement(graphml, "graph", {
			"id": chain.get("Name"),
			"edgedefault": "directed"
		})

		# Add <data> tags for <graph> tag
		for key, value in chain.attrib.items():
			if key != "Name":
				data = SubElement(graph, "data", { "key": graphml.findall("key[@attr.name='" + key.lower() + "']")[0].get("id") })
				data.text = value

		# Add <node> tags for <graph> tag
		for i, runnable in enumerate(chain.iter("Runnable")):
			node = SubElement(graph, "node", { "id": str(len(graph.findall("node"))) })

			# Add <data> tags for <node> tag
			for key, value in graph_tree.findall("Graph/Node[@Name='" + runnable.get("Name") + "']")[0].attrib.items():
				if key != "Id":
					data = SubElement(node, "data", { "key": graphml.findall("key[@attr.name='" + key.lower() + "']")[0].get("id") })
					data.text = value

			# Add <edge> tag the <node> tag and its direct predecessor
			if i != 0:
				graph.append(Element("edge", {
					"source": graph.findall("node")[i - 1].get("id"),
					"target": node.get("id")
				}))

	logging.info("Imported graph:\n" + xml.dom.minidom.parseString(tostring(graphml)).toprettyxml())

	return tostring(graphml)

def import_files_from_folder(folder_path: Path) -> Tuple[Path, Path]:
	"""Attempts to gather the required files in `folder_path`.

	Parameters
	----------
	folder_path : Path
		The `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.

	Returns
	-------
	(Path, Path)
		A pair of filepaths pointing to the `*.tsk` and `*.cfg` files.

	Raises
	------
	FileNotFoundError
		If no `*.tsk` or `*.cfg` file can be found.
	"""

	tsk = [element for element in list(folder_path.glob('**/*.tsk')) if element.is_file()][0]
	cfg = [element for element in list(folder_path.glob('**/*.cfg')) if element.is_file()][0]

	if tsk is None or cfg is None:
		raise FileNotFoundError("The folder " + folder_path.name + " include at least one *.tsk file and one *.cfg file.")

	logging.info("Files found:\n\t" + tsk.name + "\n\t" + cfg.name)

	if tsk.name[:-len(tsk.suffix)] != cfg.name[:-len(tsk.suffix)]:
		logging.warning("The names of the files mismatch: '" + tsk.name + "' and '" + cfg.name + "\'")

	return (tsk, cfg)

def problem_builder(folder_path: Path) -> Tuple[DiGraph, Architecture]:
	"""Creates a representation of the problem from the files in `folder_path`, and returns it.

	Parameters
	----------
	folder_path : Path
		The `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.

	Returns
	-------
	(DiGraph, Architecture)
		A par containing a `DiGraph` and an `Architecture` build from the files.
	"""

	filepath_pair = import_files_from_folder(folder_path)

	graph = DiGraph(parse_graphml(import_graph(filepath_pair[0])))

	if not is_directed_acyclic_graph(graph):
		raise NetworkXNotImplemented("The graph must be acyclic.")

	arch = import_arch(filepath_pair[1])

	return (graph, arch)