#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

import logging
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from queue import PriorityQueue
from typing import Iterable, List, Optional, Tuple

from datatypes import Architecture, Graph, Node, PrioritizedItem, Problem, Processor, Slice, Solution

from rate_monotonic import workload

from timed import timed_callable


# FUNCTIONS ###########################################################################################################


def _get_processes_for_core(graph: Graph, core: Tuple[int, int]) -> Optional[Iterable[Node]]:
	"""Returns an eventual list of processes scheduled on a core.

	Parameters
	----------
	graph : Graph
		An iterable of `Node`.
	core : Tuple[int, int]
		A core to look for in the processes' attributes, represented as a tuple.
		The first member is the cpu id, the second the core id.

	Returns
	-------
	Optional[List[nodes]] (should be Iterable[ref(Node)])
		A list of processes if there are any.
	"""

	return [node for node in graph if node.cpu_id == core[0] and node.core_id == core[1]]


def _get_cpuload(graph: Graph, cpu: Processor) -> Processor:
	"""Get the workload carried by the processes scheduled on a cpu, and by core.

	Parameters
	----------
	graph : Graph
		A `Graph` in which perform the search.
	cpu : Processor
		A `Processor`.

	Returns
	-------
	Processor
		A processor whose workload has been updated (inclusing its cores).
	"""

	pqueue = PriorityQueue(maxsize=len(cpu.cores))
	workload_sum = 0.0
	for core in cpu.cores:
		core = core._replace(workload=workload(_get_processes_for_core(graph, (cpu.id, core.id))))
		workload_sum += core.workload
		pqueue.put(PrioritizedItem(core.workload, core.id))

	return cpu._replace(workload=(workload_sum, pqueue))


def _node_stress(node: Node) -> Fraction:
	"""Computes the stress ratio for a node

	Parameters
	----------
	node: Node
		A `Node`.

	Returns
	-------
	Fraction
		The stress level for the `Node`.
	"""

	return Fraction(node.period - node.offset, node.wcet)


def _create_node_pqueue(graph: Graph, unassigned: bool = True) -> PriorityQueue:
	"""Creates a priority queue for all nodes in the problem, depending on the node stress.

	Parameters
	----------
	graph : Graph
		A `Graph`.
	unassigned: bool
		If set to `True`, only the `Node` objects those attribute `core_id` is `None` will be taken (default: `True`).

	Returns
	-------
	node_pqueue : PriorityQueue
		A `PriorityQueue` containing tuples of node stress and node id.
	"""

	node_pqueue = PriorityQueue(maxsize=len(graph))

	for node in filter(lambda n: n.core_id is None, graph) if unassigned else graph:
		node_pqueue.put(PrioritizedItem(_node_stress(node), node.id))

	return node_pqueue


def _update_workload(problem: Problem) -> Problem:
	"""Updates the processors workload of a problem.

	Parameters
	----------
	problem : Problem
		A `Problem`.

	Returns
	-------
	problem : Problem
		The updated `Problem`.
	"""

	with ThreadPoolExecutor(max_workers=len(problem.arch)) as executor:
		futures = [executor.submit(_get_cpuload, problem.graph, cpu) for cpu in problem.arch]
		problem = problem._replace(arch=[future.result() for future in futures])

	return problem


def _color_graphs(problem: Problem) -> List[Tuple[int, Tuple[int, int]]]:
	"""Color the graph within the problem.

	Parameters
	----------
	problem : Problem
		A `Problem`.

	Returns
	-------
	problem : Problem
		The colored `Problem`. The `core_id` attribute of all `Node` objects in `problem.graph` is assigned.
	"""

	node_pq = _create_node_pqueue(problem.graph)
	problem = _update_workload(problem)

	# while node_pq not empty
	while not node_pq.empty():
		# get first item of node_pq
		node_id = node_pq.get_nowait().item
		node = problem.graph[node_id]
		# add first core to it
		core = problem.arch[node.cpu_id].workload[1].get_nowait()
		problem.graph[node.id] = node._replace(core_id=core.item)
		problem.arch[node.cpu_id].workload[1].put_nowait(core)
		# reschedule cpu
		problem.arch[problem.graph[node_id].cpu_id] = _get_cpuload(problem.graph, problem.arch[node.cpu_id])

	return problem


def _generate_solution(problem: Problem) -> Solution:
	"""Creates and returns a solution from the relaxed problem.

	Parameters
	----------
	problem : Problem
		A `Problem`.

	Returns
	-------
	Solution
		A `Solution`.
	"""

	node_pq = _create_node_pqueue(problem.graph, False)

	while not node_pq.empty():
		node_id = node_pq.get_nowait().item
		node = problem.graph[node_id]
		# assign time slice for each process
		slices = problem.arch[node.cpu_id].cores[node.core_id].slices
		# add it to corresponding core, at the end of the list
		start = 0 if not slices else slices[-1].end + 1
		problem.arch[node.cpu_id].cores[node.core_id].slices.append(Slice(node.id, start, start + node.wcet))

	return Solution(problem.filepaths, _hyperperiod_duration(problem.arch), problem.arch)


def _hyperperiod_duration(arch: Architecture) -> int:
	"""Computes the hyperperiod length for a solution.

	Parameters
	----------
	arch : Architecture
		The `Architecture` from a `Solution`.

	Returns
	-------
	int
		The hyperperiod length for the solution.
	"""

	return max(core.slices[-1].end for cpu in arch for core in cpu.cores if core.slices)


# ENTRY POINT #########################################################################################################


@timed_callable("Solving the problem...")
def solve(problem: Problem) -> Solution:
	"""Creates the solution for a problem.

	Parameters
	----------
	problem : Problem
		A `Problem`.

	Returns
	-------
	solution : Solution
		A solution for the problem.
	"""

	# SOLVE MODEL

	problem = _color_graphs(problem)
	logging.info("Coloration found for:\t" + str(problem.filepaths))

	solution = _generate_solution(problem)
	logging.info("Solution found for:\t" + str(problem.filepaths))

	return solution
