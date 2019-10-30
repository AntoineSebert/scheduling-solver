#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# IMPORTS #############################################################################################################

from typing import NoReturn, Iterable, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue, Empty
from weakref import ref
from itertools import groupby

import logging
from timed import timed_callable
from datatypes import Problem, Solution, Slice, Chain, Graph, Node, Processor, Architecture
from rate_monotonic import workload


# FUNCTIONS ###########################################################################################################


def _chain_stress(chain: Chain) -> float:
	"""Computes the stress ratio for a chain.
	The lower that number is, the more the chain is stressed (in PriorityQueue, lowest entries are retrieved first).

	Parameters
	----------
	chain : Chain
		A sequence of tasks.

	Returns
	-------
	float
		The stress level for the chain.
	"""

	unassigned_tasks_duration = sum([node.wcet for node in chain.tasks if node.core_id == -1])
	stress = (chain.budget - sum([node.wcet for node in chain.tasks if node.core_id != -1]))

	return stress / unassigned_tasks_duration if 0 < unassigned_tasks_duration else stress


def _get_processes_for_core(graph: Graph, core: Tuple[int, int]) -> Optional[Iterable[Node]]:
	"""Returns an eventual list of processes scheduled on a core.

	Parameters
	----------
	graph : Graph
		An iterable of `Chain`.
	core : Tuple[int, int]
		A core to look for in the processes' attributes, represented as a tuple.
		The first member is the cpu id, the second the core id.

	Returns
	-------
	processes : Optional[List[nodes]] (should be Iterable[ref(Node)])
		A list of processes if there are any, or `None` otherwise.
	"""

	with ThreadPoolExecutor(max_workers=len(graph)) as executor:
		futures = [executor.submit(
			lambda chain, c: filter(lambda n: n.cpu_id == c[0] and n.core_id == c[1], chain.tasks), chain, core
		) for chain in graph]

	processes = [node for future in futures if future.result() for node in future.result()]

	return processes if processes else None


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
		pqueue.put((core.workload, core.id))

	return cpu._replace(workload=(workload_sum, pqueue))


def _create_chain_pqueue(graph: Graph) -> PriorityQueue:
	"""Creates a priority queue for all chains in the problem, depending on the chain stress.

	Parameters
	----------
	graph : Graph
		A `Graph`.

	Returns
	-------
	chain_pqueue : PriorityQueue
		A `PriorityQueue` containing tuples of chain stress and chain id.
	"""

	chain_pqueue = PriorityQueue(maxsize=len(graph))
	with ThreadPoolExecutor(max_workers=len(graph)) as executor:
		futures = {chain.id: executor.submit(_chain_stress, chain) for chain in graph}

	for chain_id, future in futures.items():
		chain_pqueue.put((future.result(), chain_id))

	return chain_pqueue


def _update_workload(problem: Problem):
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
		problem = problem._replace(arch = [future.result() for future in futures])

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

	chain_pq = _create_chain_pqueue(problem.graph)
	problem = _update_workload(problem)

	# while chain_pq not empty
	while not chain_pq.empty():
		# get first item of chain_pq
		chain_id = chain_pq.get_nowait()[1]
		# get first item of process list without core
		#print("node:", [node for node in problem.graph[chain_id].tasks if node.core_id is None][0])
		node = [node for node in problem.graph[chain_id].tasks if node.core_id is None][0]
		#for node in [node for node in problem.graph[chain_id].tasks if node.core_id is None]:
		# get first core from proc_workload with the same processor
		try:
			# add process to it
			core = problem.arch[node.cpu_id].workload[1].get_nowait()
			problem.graph[chain_id].tasks[node.id] = node._replace(core_id=core[1])
			problem.arch[node.cpu_id].workload[1].put_nowait(core)
			# reschedule cpu
			problem.arch[problem.graph[chain_id].tasks[node.id].cpu_id] = _get_cpuload(problem.graph, problem.arch[node.cpu_id])
		except Empty:
			pass

		# if at least one node not scheduled, put chain back in chain_pq
		for node in problem.graph[chain_id].tasks:
			if node.core_id is None:
				chain_pq.put_nowait((_chain_stress(problem.graph[chain_id]), chain_id))
				break

	return problem


def _theoretical_scheduling_time(chain: Chain) -> int:
	"""Computes the theoretical scheduling time of a sequence of tasks.

	Parameters
	----------
	chain : Chain
		A `Chain`.

	Returns
	-------
	int
		The theoretical shortest scheduling time for the chain.
	"""

	return sum([node.wcet for node in chain.tasks])


def _shortest_theoretical_scheduling(graph: Graph) -> int:
	"""Computes the shortest theoretical scheduling time from the longest scheduling path of all chain.

	Parameters
	----------
	graph : Graph
		A `Graph`.

	Returns
	-------
	int
		The theoretical shortest scheduling time for the graph.
	"""

	return min([sum([node.wcet for node in chain.tasks]) for chain in graph])


def _schedule_chain(chain: Chain, arch: Architecture) -> NoReturn:
	"""Schedules the tasks from a chain on the cores they have been assigned.

	Parameters
	----------
	chain : Chain
		A `Chain` to schedule.
	arch : Architecture
		A `Architecture` where to schedule the tasks of the chain.
	"""

	# for each process in chain
	for node in chain.tasks:
		# assign time slice for each process
		slices = arch[node.cpu_id].cores[node.core_id].slices
		# add it to corresponding core, at the end of the list
		start = 0 if not slices else slices[-1].end
		slices.append(Slice(task=(chain.id, node.id), start=start, end=start + node.wcet))


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

	# group graphs by desc priority level
	for keyvalue, chain_group in groupby(problem.graph, lambda chain: chain.priority):
		# for each priority level, sort by descending chain length
		for chain in reversed(sorted(list(chain_group), key=lambda chain: len(chain))):
			_schedule_chain(chain, problem.arch)

	return (_hyperperiod_duration(problem.arch), problem.arch)


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

	return max([core.slices[-1].end for cpu in arch for core in cpu.cores if core.slices])


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

	logging.info("Theoretical shortest scheduling time:\t" + str(_shortest_theoretical_scheduling(problem.graph)) + "ms.")

	problem = _color_graphs(problem)
	logging.info("Coloration found for" + problem.name)

	solution = _generate_solution(problem)
	logging.info("Solution found for" + problem.name)

	return solution
