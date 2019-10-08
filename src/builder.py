#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import List, Callable, FrozenSet, Tuple
import logging
from pathlib import Path
import xml.etree.cElementTree as et

from networkx import DiGraph
from networkx.readwrite.graphml import read_graphml
from networkx.algorithms.dag import is_directed_acyclic_graph

from type_aliases import Architecture

# FUNCTIONS ###########################################################################################################

"""Create the processor architecture from the configuration file.

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
import_arch: Callable[[Path], Architecture] = lambda filepath: [[core.attrib["MacroTick"] for core in corelist] for corelist in [cpu.findall('Core') for cpu in et.parse(filepath).findall("Cpu")]]

def import_graph(filepath: Path) -> int:
	for cpu in et.parse(filepath).find("graph").iter():
		print(cpu)

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

	logging.getLogger("main_logger").info("Files found:\n\t" + tsk.name + "\n\t" + cfg.name)

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

	logging.getLogger("main_logger").info("Gathering the required files...")
	filepath_pair = import_files_from_folder(folder_path)
	logging.getLogger("main_logger").info("Done.")

	logging.getLogger("main_logger").info("Generating graph from  the '.tsk' file...")
	graph = DiGraph(read_graphml(import_graph(filepath_pair[0])))
	if not is_directed_acyclic_graph(graph):
		raise NetworkXNotImplemented("The graph must be acyclic.")
	logging.getLogger("main_logger").info("Done.")

	logging.getLogger("main_logger").info("Generating architecture from the '.cfg' file...")
	arch = import_arch(filepath_pair[1])
	logging.getLogger("main_logger").info("Done.")

	"""
	# test if architecture is valid
	if len(arch) == 0:
		raise NoProcessor("The configuration must include at least one processor.")

	# display
	print("Number of cores and processors: ")
	print("\t", *arch)

	# print target
	print("Theoretical shortest scheduling time:")
	sched_time = 0
	longest_path = dag_longest_path(G)
	for i in range(0, len(longest_path) - 1):
		node = longest_path[i]
		sched_time += G.nodes(data=True)[node]['wcet'] + G.edges[node, longest_path[i + 1]]['weight']
	sched_time += G.nodes(data=True)[longest_path[-1]]['wcet']
	print("\t", sched_time)
	"""