#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################


from dataclasses import dataclass, field
from fractions import Fraction
from json import JSONEncoder
from pathlib import Path
from queue import PriorityQueue
from typing import Any, Iterable, NamedTuple, Optional

from ortools.sat.python.cp_model import CpModel

from recordclass import RecordClass


# TYPE ALIASES ########################################################################################################


class Slice(RecordClass):
	"""Named tuple representing an execution slice of a task.

	Attributes
	----------
	task_id : int (should be: ref(Node))
		The reference to the task.
	start : int
		The start time of the slice.
	end : int
		The end time of the slice.
	"""

	task_id: int
	start: int
	end: int


class Core(RecordClass):
	"""Named tuple representing a core.

	Attributes
	----------
	id : int
		The core id within a `Processor`.
	macrotick : Optional[int]
		The macrotick of the core.
	workload : Fraction
		The workload carried by the `Node` objects in `slices`.
	slices : Iterable[Slice] (can be empty)
		The execution slices of the `Node` objects scheduled on this core.
	"""

	id: int
	macrotick: Optional[int]
	workload: Fraction
	slices: Iterable[Slice]


class Processor(RecordClass):
	"""Named tuple representing a processor.

	Attributes
	----------
	id : int
		The processor within an `Architecture`.
	workload : Tuple[Fraction, PriorityQueue] (PriorityQueue contains core ids, should be: ref(core))
		A tuple containing the workload carried by the eventual `Node` objects scheduled on the cores of this processor,
		and a priority queue of `Core` ids by ascending order of workload.
	cores : Iterable[Core]
		The iterable containing the `Core` objects within the Processor.
	"""

	id: int
	workload: int
	cores: Iterable[Core]


"""An iterable of `Processor` representing an `Architecture`."""
Architecture = Iterable[Processor]


class Node(RecordClass):
	"""A node representing a task.

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

	id: int
	name: str
	wcet: int
	period: int
	deadline: int
	max_jitter: Optional[int]
	offset: int
	cpu_id: int
	core_id: Optional[int]


"""An iterable of `Node` representing a `Graph`."""
Graph = Iterable[Node]


class Filepath_pair(NamedTuple):
	"""Holds a `Filepath_pair` to a `*.tsk` and a `*.cfg` file, representing a test case.

	Attributes
	----------
	tsk : Path
		A `Path` to a `*.tsk` file.
	cfg : Path
		A `Path` to a `*.cfg` file.
	"""

	tsk: Path
	cfg: Path


class Problem(RecordClass):
	"""A problem holding a `Filepath_pair`, a `Graph`, an architecture.

	Attributes
	----------
	filepaths : Filepath_pair
		The `Filepath_pair` from which the `Problem` has been generated.
	graph : Graph
		A `Graph` containing task sequences.
	arch : Architecture
		An `Architecture` containing a sequence of `Processor`.
	model : CpModel
		A `CpModel` object that holds the variables and contraints. Meant to replace `graph` and `arch` in the future.
	"""

	filepaths: Filepath_pair
	graph: Graph
	arch: Architecture
	model: CpModel


class Solution(RecordClass):
	"""A solution holding an hyperperiod as `int`, and an architecture as Architecture (should be: `ref(Architecture)`).

	Attributes
	----------
	filepaths : Filepath_pair
		The `Filepath_pair` from which the `Solution` has been generated.
	hyperperiod : int
		The hyperperiod length for this `Solution`.
	arch : Architecture
		An `Architecture` containing a sequence of `Processor`.
	"""

	filepaths: Filepath_pair
	hyperperiod: int
	arch: Architecture


class PriorityQueueEncoder(JSONEncoder):
	"""An encoder dedicated to parse `PriorityQueue` objects into JSON.

	Methods
	-------
	default(obj)
		Returns a list containing the size of the `PriorityQueue` and a boolean whether it is empty or not.
	"""

	def default(self, obj):
		if isinstance(obj, PriorityQueue):
			return [obj.qsize(), obj.empty()]
		# Let the base class default method raise the TypeError
		return JSONEncoder.default(self, obj)


@dataclass(order=True)
class PrioritizedItem:
	"""An encoder dedicated to parse `PriorityQueue` objects into JSON.

	Attributes
	----------
	priority : Fraction
		The prioroty of the element as a `Fraction`.
	item : Any
		The data carried by the element. This field is not taken into account for the prioritization.
		(default: `field(compare=False)`)
	"""

	priority: Fraction
	item: Any = field(compare=False)
