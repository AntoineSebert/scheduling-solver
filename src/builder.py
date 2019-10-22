#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from pathlib import Path
from typing import List, Tuple, NoReturn, Mapping, Iterable, Dict
import xml.etree.ElementTree as et
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from concurrent.futures import ThreadPoolExecutor

from networkx import DiGraph, NetworkXNotImplemented
from networkx.algorithms.dag import is_directed_acyclic_graph
from networkx.readwrite.graphml import parse_graphml, generate_graphml

from datatypes import Architecture, Problem
from timed import timed_callable


# FUNCTIONS ###########################################################################################################


@timed_callable("Generating architecture from the '.cfg' file...")
def _import_arch(filepath: Path) -> Architecture:
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


def _insert_node_keys(graphml: Element, attributes: Mapping[str, str]) -> NoReturn:
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


def _get_keys(tree: ElementTree, paths: Iterable[Tuple[str, str]]) -> Dict[str, str]:
	"""Returns the attributes found in the first <graph> tag

	Parameters
	----------
	tree : ElementTree
		A <graphml> root tag.
	attributes : Iterable[Tuple[str, str]]
		An iterable containing tuples of paths where to look up and destinations (an alias for the paths).

	Returns
	-------
		Dict[str, str]
			A dictionary of containing destinations as values and lists of <key> tags as attributes.
	"""

	attributes = dict()

	for path, dest in paths:
		keys = list()
		for attribute, _ in tree.find(path).attrib.items():
			key = Element("key", {
				"id": dest + str(len(keys)),
				"for": dest,
				"attr.name": attribute.lower(),
				"attr.type": "string" if attribute == "Name" else "int"
			})

			if attribute != "Name":
				default = SubElement(key, "default")
				default.text = "-1" if attribute == "MaxJitter" or attribute == "CoreId" else "0"
			keys.append(key)

		if keys:
			attributes[dest] = keys

	return attributes


@timed_callable("Generating graph from  the '.tsk' file...")
def _import_graph(filepath: Path) -> List[str]:
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
	graphml_keys = _get_keys(graph_tree, [("Graph/Chain", "chain"), ("Graph/Node", "node")])

	# Add <graph> tags and their children <data>, <node> and <edge>
	for chain in graph_tree.iter("Chain"):
		# Add <graphml> document root
		graph_list.append(Element("graphml", {
			"xmlns": "http://graphml.graphdrawing.org/xmlns",
			"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
			"xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.1/graphml.xsd"
		}))

		# Add keys
		for key in graphml_keys.get("chain"):
			graph_list[-1].append(key)
		for key in graphml_keys.get("node"):
			graph_list[-1].append(key)

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


def _import_files_from_folder(folder_path: Path) -> Tuple[Path, Path]:
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

	tsk = next(filter(Path.is_file, folder_path.glob('*.tsk')))
	cfg = next(filter(Path.is_file, folder_path.glob('*.cfg')))

	if tsk.stem != cfg.stem:
		logging.warning("The names of the files mismatch: '" + tsk.stem + "' and '" + cfg.stem + "'")

	return (tsk, cfg)


@timed_callable("Gathering the required files...")
def _get_filepath_pairs(folder_path: Path, recursive: bool = False) -> List[Tuple[Path, Path]]:
	"""Attempts to gather the required files in `folder_path`.

	Parameters
	----------
	folder_path : Path
		A `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.
	recursive: bool
		Toggles the recursive search for cases (default: False).
		All the folders and subfolders containing at least one `*.tsk` and `*.cfg` file will be taken.

	Returns
	-------
	List[Tuple[Path, Path]]
		A list of pair containg two paths, to a `*.tsk` and `*.cfg` file
	"""

	filepath_pairs = list()

	try:
		filepath_pairs.append(_import_files_from_folder(folder_path))
	except StopIteration:
		pass

	if recursive:
		for subfolder in filter(lambda e: e.is_dir(), folder_path.iterdir()):
			try:
				filepath_pairs += _get_filepath_pairs(subfolder, True)
			except StopIteration:
				pass

	return filepath_pairs


def _build_single_problem(filepath_pair: Tuple[Path, Path]) -> Problem:
	"""Creates the solution for a problem.

	Parameters
	----------
	filepath_pair : Tuple[Path, Path]
		A pair of filepaths pointing to the `*.tsk` and `*.cfg` files.

	Returns
	-------
	Problem
		A problem generated from the test case.

	Raises
	------
	NetworkXNotImplemented
		If one of the graphs contains a cycle.
	"""

	logging.info("Files found:\n\t" + filepath_pair[0].name + "\n\t" + filepath_pair[1].name)

	graph_list = [DiGraph(parse_graphml(graph)) for graph in _import_graph(filepath_pair[0])]
	for graph in graph_list:
		if not is_directed_acyclic_graph(graph):
			raise NetworkXNotImplemented("The graphs must be acyclic.")
	logging.info("Imported graphs:\n" + '\n'.join(['\n'.join(generate_graphml(graph)) for graph in graph_list]))

	architecture = _import_arch(filepath_pair[1])
	logging.info("Imported architecture:\n\t" + '\n\t'.join(','.join(cpu) for cpu in architecture))

	return Problem(name=str(filepath_pair[0]), graphs=graph_list, arch=architecture)


# ENTRY POINT #########################################################################################################


def problem_builder(folder_path: Path, recursive: bool) -> List[Problem]:
	"""Creates a representation of the problem from the files in `folder_path`, and returns it.

	Parameters
	----------
	folder_path : Path
		A `Path` from which import the `*.tsk` and `*.cfg` files.
		Only the first encountered file of each type is taken, all the others are ignored.
	recursive: bool
		Toggles the recursive search for cases.
		All the folders and subfolders containing at least one `*.tsk` and `*.cfg` file will be taken.

	Returns
	-------
	List[Problem]
		A list of `Problem`.

	Raises
	------
	FileNotFoundError
		If not pair of `*.tsk` and `*.cfg` files can be found.
	"""

	filepath_pairs = _get_filepath_pairs(folder_path, recursive)

	if not filepath_pairs:
		raise FileNotFoundError("No matching files found. At least one *.tsk file and one *.cfg file are necessary.")

	futures = list()

	with ThreadPoolExecutor(max_workers=len(filepath_pairs)) as executor:
		futures = [executor.submit(_build_single_problem, filepath_pair) for filepath_pair in filepath_pairs]

	return [future.result() for future in futures]
