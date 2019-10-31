#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from typing import Iterable, Tuple
from collections import namedtuple


# TYPE ALIASES ########################################################################################################

"""Named tuple representing an execution slice of a task.

Attributes
----------
task : Tuple[int, int] (should be: ref(Node))
	The reference to the task.
start : int
	The start time of the slice.
end : int
	The end time of the slice.
"""
Slice = namedtuple('Slice', ['task', 'start', 'end'])

"""Named tuple representing a core within a processor.

Attributes
----------
id : int
	The core id within a `Processor`.
macrotick : Optional[int]
	The macrotick of the core.
workload : float (0.0 by default)
	The workload carried by the `Node` objects in `slices`.
slices : Iterable[Slice] (can be empty)
	The execution slices of the `Node` objects scheduled on this core.
"""
Core = namedtuple("Core", ["id", "macrotick", "workload", "slices"])

"""Named tuple representing a processor within an architecture.

Attributes
----------
id : int
	The processor within an `Architecture`.
workload : Tuple[float, PriorityQueue] (PriorityQueue contains core ids, should be: ref(core))
	A tuple containing the workload carried by the eventual `Node` objects scheduled on the cores of this processor,
	and a priority queue of `Core` ids by ascending order of workload.
cores : Iterable[Core]
	The iterable containing the `Core` objects within the Processor.
"""
Processor = namedtuple('Processor', ["id", "workload", "cores"])

"""An iterable of `Processor` representing an `Architecture`."""
Architecture = Iterable[Processor]

"""A node representing a task within a chain.

Attributes
----------
id : int
	The node id within a `Chain`.
name : str
	The name of the node. May not be unique.
wcet : int
	The WCET of the node. Cannot be `0.0`.
period : int
	The period of the node. Cannot be `0.0`.
deadline : int
	The deadline of the node.
max_jitter : Optional[int]
	The eventual jitter of the node.
offset : int
	The start offset of the node.
cpu_id : int (should be: ref(Processor))
	A `Processor` the node is scheduled on. Cannot be None.
core_id : Optional[int] (should be: Optional[ref(Core)])
	A `Core` within a `Processor` the node is scheduled on.
"""
Node = namedtuple("Node", ["id", "name", "wcet", "period", "deadline", "max_jitter", "offset", "cpu_id", "core_id"])

"""A chain representing a task sequence within a graph.

Attributes
----------
id : int
	The chain id within a `Graph`. (Note: not equivalent to the attribute <Chain/name>).
budget : int
	The bugdet of the chain. Cannot be `0`.
priority : int (actually bool)
	The priority of the Chain, either 0 (lower) or 1 (higher).
	Represented as an integer to offer support for wider range of priority.
tasks : Iterable[Node] (cannot be empty)
	An iterable of `Node`, representing the tasks of the sequence.
"""
Chain = namedtuple("Chain", ["id", "budget", "priority", "tasks"])

"""An iterable of `Chain` representing an `Graph`."""
Graph = Iterable[Chain]

"""A problem holding a graph and an architecture.

Attributes
----------
filepaths : Filepaths
	The `Filepaths` from which the problem has been generated.
graph : Graph
	A `Graph` containing task sequences.
arch : Architecture
	An `Architecture` containing a sequence of `Processor`.
"""
Problem = namedtuple("Problem", ["filepaths", "graph", "arch"])

"""A solution holding an hyperperiod as `int`, and an architecture as Architecture (should be: `ref(Architecture)`)."""
Solution = Tuple[int, Architecture]

"""Holds two filepaths to a `*.tsk` and a `*.cfg` file, representing a test case.

Attributes
----------
tsk : Path
	A `Path` to a `*.tsk` file.
cfg : Path
	A `Path` to a `*.cfg` file.
"""
Filepaths = namedtuple("Filepaths", ["tsk", "cfg"])
